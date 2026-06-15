#!/usr/bin/env python3
"""
Validate `.claude/context/**/*.xml` against the schema and repo conventions.

This script is intended to be portable with the `.claude/` folder when copied
into downstream project repositories.

Checks performed:
- XML well-formedness
- XSD validation (via `xmllint`)
- Required file metadata attributes and uniqueness (`CTX-...` ids)
- Rule id rules and uniqueness
- Referential integrity:
  - all `<doc_ref path="..."/>` targets exist
  - all `<ref id="..."/>` resolve to exactly one rule id (unless TODO-marked)
- Deterministic canonical formatting (and a `--fix` mode to auto-apply it)
- Structural guardrails (e.g., no `anchor` attributes; rules use `<desc>` child)

Usage:
  - Fail-only (CI / pre-commit): `python3 .claude/tools/context/validate_context.py`
  - Auto-fix formatting: `python3 .claude/tools/context/validate_context.py --fix`
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from context_xml import canonical_xml_string, iter_xml_files

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTEXT_ROOT = REPO_ROOT / ".claude" / "context"
SCHEMA_PATH = CONTEXT_ROOT / "schema" / "context.xsd"

FILE_ID_RE = re.compile(r"^CTX-[A-Z0-9-]+$")
RULE_ID_STRICT_RE = re.compile(r"^[A-Z]{1,2}\d{3}-[A-Z0-9-]+$")
GROUP_ID_RE = re.compile(r"^(?:[A-Z]{1,2}\dxx|[A-Z]{1,2}\d{2}x)$")
ENTRY_ID_RE = re.compile(r"^[A-Z0-9-]+$")


class InvalidXmlError(ValueError):
    """Raised when a context XML file is not valid XML."""

    def __init__(self, details: str) -> None:
        """Create an invalid-XML error."""
        super().__init__(f"Invalid XML: {details}")


@dataclass(frozen=True)
class RefIssue:
    """
    A reference integrity issue discovered while validating `<ref id="..."/>` nodes.
    """

    file: Path
    ref_id: str
    message: str


def _xmllint_schema_validate(path: Path) -> list[str]:
    cmd = [
        "xmllint",
        "--noout",
        "--schema",
        str(SCHEMA_PATH),
        str(path),
    ]
    proc = subprocess.run(  # noqa: S603
        cmd, check=False, capture_output=True, text=True
    )
    if proc.returncode == 0:
        return []
    out = (proc.stderr or "").strip()
    return [out] if out else [f"xmllint schema validation failed for {path}"]


def _parse_xml(path: Path) -> ET.Element:
    try:
        return ET.parse(path).getroot()  # noqa: S314
    except (ET.ParseError, OSError) as e:
        raise InvalidXmlError(str(e)) from e


def _resolve_doc_ref(base_file: Path, doc_ref_path: str) -> Path:
    return (base_file.parent / doc_ref_path).resolve()


def _normalize_ws(value: str) -> str:
    return " ".join(value.split())


def _has_adjacent_todo(
    parent: ET.Element, child: ET.Element, *, kind: str, target: str
) -> bool:
    kids = list(parent)
    try:
        idx = kids.index(child)
    except ValueError:
        return False
    for j in (idx - 1, idx + 1):
        if 0 <= j < len(kids):
            sib = kids[j]
            if (
                sib.tag == "todo"
                and (sib.get("kind") or "") == kind
                and (sib.get("target") or "") == target
            ):
                return True
    return False


def main(argv: list[str]) -> int:  # noqa: C901, PLR0912, PLR0915
    """
    CLI entrypoint.

    Returns a process exit code:
    - 0: all checks pass
    - 1: validation failed
    - 2: configuration/environment error (missing context/schema)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fail-on-todos",
        action="store_true",
        help="Treat TODO-marked issues as failures.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Rewrite context XML files into canonical formatting (format-only).",
    )
    args = parser.parse_args(argv)

    if not CONTEXT_ROOT.exists():
        sys.stderr.write(f"context root not found: {CONTEXT_ROOT}\n")
        return 2
    if not SCHEMA_PATH.exists():
        sys.stderr.write(f"schema not found: {SCHEMA_PATH}\n")
        return 2

    xml_files = list(iter_xml_files(CONTEXT_ROOT))
    if not xml_files:
        sys.stderr.write("no context xml files found\n")
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    # Parse.
    roots: dict[Path, ET.Element] = {}
    for path in xml_files:
        try:
            roots[path] = _parse_xml(path)
        except ValueError as e:
            errors.append(f"ERROR: {path}: {e}")

    # Auto-fix (format-only): strip forbidden attrs and rewrite canonical XML.
    if args.fix and not errors:
        fixed = 0
        for path, root in roots.items():
            changed = False
            for el in root.iter():
                if "anchor" in el.attrib:
                    el.attrib.pop("anchor", None)
                    changed = True

            canonical = canonical_xml_string(root)
            existing = path.read_text(encoding="utf-8")
            if existing != canonical:
                path.write_text(canonical, encoding="utf-8")
                changed = True
            if changed:
                fixed += 1

        # Re-parse after rewrites to ensure schema validation applies to final content.
        roots = {}
        for path in xml_files:
            try:
                roots[path] = _parse_xml(path)
            except ValueError as e:
                errors.append(f"ERROR: {path}: {e}")
        if fixed:
            sys.stdout.write(f"Fixed {fixed} XML files.\n")

    # Schema validate via xmllint.
    for path in xml_files:
        errors.extend(
            f"ERROR: {path}: schema validation failed:\n{msg}"
            for msg in _xmllint_schema_validate(path)
        )

    # File-level ID uniqueness.
    file_ids: dict[str, Path] = {}
    for path, root in roots.items():
        fid = (root.get("id") or "").strip()
        if not fid:
            errors.append(f"ERROR: {path}: missing root @id")
            continue
        if not FILE_ID_RE.fullmatch(fid):
            errors.append(
                f"ERROR: {path}: root @id must match {FILE_ID_RE.pattern}: '{fid}'"
            )
        if fid in file_ids:
            errors.append(
                f"ERROR: duplicate file id '{fid}': {file_ids[fid]} and {path}"
            )
        else:
            file_ids[fid] = path
        if "anchor" in root.attrib:
            errors.append(f"ERROR: {path}: root must not have @anchor")

    # Collect all rule IDs globally (definitions only).
    rule_defs: dict[str, Path] = {}
    for path, root in roots.items():
        if root.tag != "rules":
            continue
        for rule in root.findall("./rule[@id]"):
            rid = (rule.get("id") or "").strip()
            if not rid:
                continue
            if not RULE_ID_STRICT_RE.fullmatch(rid):
                errors.append(
                    "ERROR: "
                    f"{path}: invalid rule @id (must be uppercase alnum + '-'): "
                    f"'{rid}'"
                )
                continue
            if "anchor" in rule.attrib:
                errors.append(f'ERROR: {path}: <rule id="{rid}"> must not have @anchor')
            if "desc" in rule.attrib:
                errors.append(
                    f'ERROR: {path}: <rule id="{rid}"> must not have @desc attribute '
                    "(use <desc> child)"
                )

            desc_children = list(rule.findall("./desc"))
            if len(desc_children) != 1:
                errors.append(
                    f'ERROR: {path}: <rule id="{rid}"> must contain exactly one <desc> '
                    "element"
                )
            else:
                desc_text = (desc_children[0].text or "").strip()
                if not desc_text:
                    errors.append(
                        f'ERROR: {path}: <rule id="{rid}"> <desc> must be non-empty'
                    )

            for note in rule.findall("./notes/note[@title='desc']"):
                note_text = (note.text or "").strip()
                if note_text:
                    errors.append(
                        "ERROR: "
                        f"{path}: <rule id=\"{rid}\"> has notes/note@title='desc' "
                        "(likely a migration glitch); move this text into <desc> and "
                        "delete the note"
                    )

            if rid in rule_defs:
                errors.append(
                    f"ERROR: duplicate rule id '{rid}': {rule_defs[rid]} and {path}"
                )
            else:
                rule_defs[rid] = path

    # Disallow anchor attributes anywhere.
    for path, root in roots.items():
        errors.extend(
            f"ERROR: {path}: element <{el.tag}> must not have @anchor"
            for el in root.iter()
            if "anchor" in el.attrib
        )

    # Ensure single-line <example> leaf nodes do not end with a trailing newline.
    for path, root in roots.items():
        if root.tag != "rules":
            continue
        for example in root.findall(".//example"):
            if list(example):
                continue
            txt = example.text or ""
            if not txt.endswith("\n"):
                continue
            trimmed = txt.rstrip("\n")
            if trimmed and "\n" not in trimmed:
                errors.append(
                    "ERROR: "
                    f"{path}: <example> single-line text ends with newline; run "
                    "formatter to inline closing tag"
                )

    # Validate grouping/entry ids (indexes/manifests).
    for path, root in roots.items():
        for el in root.iter():
            if "id" not in el.attrib:
                continue
            val = (el.get("id") or "").strip()
            if not val:
                continue
            if el.tag == "rule":
                continue
            if el.tag == root.tag:
                continue
            if (
                RULE_ID_STRICT_RE.fullmatch(val)
                or GROUP_ID_RE.fullmatch(val)
                or ENTRY_ID_RE.fullmatch(val)
            ):
                continue
            errors.append(f"ERROR: {path}: invalid id '{val}' on <{el.tag}>")

    # Validate doc_ref paths exist.
    for path, root in roots.items():
        for doc_ref in root.findall(".//doc_ref[@path]"):
            rel = (doc_ref.get("path") or "").strip()
            if not rel:
                errors.append(f"ERROR: {path}: <doc_ref> missing @path")
                continue
            target = _resolve_doc_ref(path, rel)
            if not target.exists():
                errors.append(f"ERROR: {path}: doc_ref path does not exist: {rel}")

    # Enforce index label <-> rules title consistency and guard against duplicates.
    rules_title_by_parent: dict[tuple[Path, str], Path] = {}
    for path, root in roots.items():
        if root.tag != "rules":
            continue
        title = _normalize_ws((root.get("title") or "").strip())
        if not title:
            continue
        key = (path.parent, title.casefold())
        existing = rules_title_by_parent.get(key)
        if existing is not None and existing != path:
            errors.append(
                "ERROR: duplicate rules title within directory "
                f"'{title}': {existing} and {path}"
            )
        else:
            rules_title_by_parent[key] = path

    rules_target_label: dict[Path, str] = {}
    for path, root in roots.items():
        if root.tag != "index":
            continue

        labels_in_index: dict[str, str] = {}
        for entry in root.findall(".//entry"):
            label_raw = (entry.get("label") or "").strip()
            doc_ref = entry.find("./doc_ref")
            doc_ref_path = (
                (doc_ref.get("path") or "").strip() if doc_ref is not None else ""
            )
            if not label_raw or not doc_ref_path:
                continue

            target = _resolve_doc_ref(path, doc_ref_path)
            target_root = roots.get(target)
            if target_root is None or target_root.tag != "rules":
                continue

            label = _normalize_ws(label_raw)
            label_key = label.casefold()
            prior = labels_in_index.get(label_key)
            if prior is not None:
                errors.append(
                    "ERROR: "
                    f"{path}: duplicate entry labels (case-insensitive) in index: "
                    f"'{prior}' and '{label}'"
                )
            else:
                labels_in_index[label_key] = label

            title = _normalize_ws((target_root.get("title") or "").strip())
            if title != label:
                errors.append(
                    "ERROR: "
                    f"{path}: entry label '{label}' does not match target rules title "
                    f"'{title}' in {target}"
                )

            seen = rules_target_label.get(target)
            if seen is not None and seen != label:
                errors.append(
                    f"ERROR: inconsistent labels for {target}: '{seen}' vs '{label}'"
                )
            else:
                rules_target_label[target] = label

    # Validate refs resolve uniquely; allow TODO-marked unresolved refs.
    unresolved: list[RefIssue] = []
    for path, root in roots.items():
        for parent in root.iter():
            for ref in list(parent):
                if ref.tag != "ref":
                    continue
                rid = (ref.get("id") or "").strip()
                if not rid:
                    errors.append(f"ERROR: {path}: <ref> missing @id")
                    continue
                if not RULE_ID_STRICT_RE.fullmatch(rid):
                    errors.append(
                        f'ERROR: {path}: <ref id="{rid}"> must be uppercase alnum + '
                        "hyphen (-)"
                    )
                    continue
                if rid not in rule_defs:
                    if _has_adjacent_todo(
                        parent, ref, kind="unresolved-ref", target=rid
                    ):
                        unresolved.append(
                            RefIssue(
                                file=path, ref_id=rid, message="TODO unresolved-ref"
                            )
                        )
                        continue
                    errors.append(f"ERROR: {path}: unresolved ref id: {rid}")

    if unresolved:
        msg = "\n".join(
            f"WARN: {i.file}: unresolved ref (TODO): {i.ref_id}" for i in unresolved
        )
        warnings.append(msg)
        if args.fail_on_todos:
            errors.append(
                "ERROR: unresolved refs with TODOs present (--fail-on-todos)."
            )

    # Canonical formatting check.
    for path, root in roots.items():
        try:
            canonical = canonical_xml_string(root)
        except (ValueError, TypeError) as e:
            errors.append(f"ERROR: {path}: canonicalization failed: {e}")
            continue
        existing = path.read_text(encoding="utf-8")
        if existing != canonical:
            diff = difflib.unified_diff(
                existing.splitlines(),
                canonical.splitlines(),
                fromfile=str(path),
                tofile=str(path),
                lineterm="",
            )
            errors.append("ERROR: non-canonical formatting:\n" + "\n".join(diff))

    if warnings:
        sys.stderr.write("\n".join(warnings) + "\n")
    if errors:
        sys.stderr.write("\n".join(errors) + "\n")
        return 1

    sys.stdout.write(f"OK: validated {len(xml_files)} XML files under {CONTEXT_ROOT}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
