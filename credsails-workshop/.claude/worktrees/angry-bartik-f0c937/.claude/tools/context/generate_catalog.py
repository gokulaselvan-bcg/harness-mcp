#!/usr/bin/env python3
"""
Generate per-language coding standards catalogs from XML sources.

Sources (under .claude/context/coding-standards/<language>/):
- index.xml: hundreds-level metadata (label/desc/path)
- */index.xml: tens-level metadata (label/desc/path)
- rule XML files (*.xml): one or more <rule id="..." desc="..."/> elements

Output:
- index-catalog.xml (minified) per language folder.

Strictness:
- Missing/invalid metadata for any required hundreds/tens (implied by rules) is an
  error.
- Missing/invalid rule id/desc is an error.
- Any errors => non-zero exit, with actionable fix instructions.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from context_xml import canonical_xml_string

REPO_ROOT = Path(__file__).resolve().parents[3]
CODING_STANDARDS_DIR = REPO_ROOT / ".claude" / "context" / "coding-standards"

RULE_ID_RE = re.compile(r"^([A-Z]{1,2})(\d{3})-[A-Z0-9-]+$")
HUNDREDS_ID_RE = re.compile(r"^[A-Z]{1,2}\dxx$")
TENS_ID_RE = re.compile(r"^[A-Z]{1,2}\d{2}x$")


class InvalidRuleIdError(ValueError):
    """Raised when a rule id does not match the required format."""

    def __init__(self, rule_id: str) -> None:
        """Create an exception describing an invalid rule id."""
        super().__init__(f"Invalid rule id: {rule_id}")


@dataclass(frozen=True)
class Rule:
    """A discovered rule within a language pack."""

    rule_id: str
    desc: str
    rel_path: str  # relative to language root


@dataclass(frozen=True)
class Meta:
    """Metadata for a hundreds/tens entry from an index.xml."""

    entry_id: str
    label: str
    desc: str
    target_path: Path  # absolute path


def _parse_rule_id(rule_id: str) -> tuple[str, int]:
    m = RULE_ID_RE.match(rule_id)
    if not m:
        raise InvalidRuleIdError(rule_id)
    return (m.group(1), int(m.group(2)))


def _hundreds_id(prefix: str, number: int) -> str:
    return f"{prefix}{number // 100}xx"


def _tens_id(prefix: str, number: int) -> str:
    return f"{prefix}{number // 10:02d}x"


def _is_guideline_prefix(prefix: str) -> bool:
    return prefix.endswith("Y")


def _log_error(errors: list[str], *, where: str, problem: str, fix: str) -> None:
    errors.append(f"ERROR: {where}: {problem}\n  Fix: {fix}")


def _write_if_changed(path: Path, content: str, *, check: bool) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if existing == content:
        return
    if check:
        diff = difflib.unified_diff(
            existing.splitlines(),
            content.splitlines(),
            fromfile=str(path),
            tofile=str(path),
            lineterm="",
        )
        sys.stderr.write("\n".join(diff) + "\n")
        raise SystemExit(1)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _posix_relpath(path: Path, start: Path) -> str:
    return Path(os.path.relpath(path, start=start)).as_posix()


def _parse_index_entries(
    *,
    index_xml: Path,
    errors: list[str],
    expected_kind: str,
    id_re: re.Pattern[str],
) -> dict[str, Meta]:
    """
    Parse <entry kind="..."> from index.xml.

    Required attributes: id, label, desc, path.
    """
    try:
        tree = ET.parse(index_xml)  # noqa: S314
    except (ET.ParseError, OSError) as e:
        _log_error(
            errors,
            where=str(index_xml),
            problem=f"Invalid XML: {e}",
            fix="Fix XML well-formedness (unclosed tags, invalid characters).",
        )
        return {}

    root = tree.getroot()
    entries: dict[str, Meta] = {}
    for entry in root.findall(".//entry"):
        kind = (entry.get("kind") or "").strip()
        if kind != expected_kind:
            continue
        entry_id = (entry.get("id") or "").strip()
        label = (entry.get("label") or "").strip()
        desc = (entry.get("desc") or "").strip()
        rel_path = (entry.get("path") or "").strip()
        if not rel_path:
            doc_ref = entry.find("doc_ref")
            if doc_ref is not None:
                rel_path = (doc_ref.get("path") or "").strip()

        if not entry_id or not id_re.match(entry_id):
            _log_error(
                errors,
                where=str(index_xml),
                problem=f"Missing/invalid {expected_kind} id on <entry>: '{entry_id}'.",
                fix=(
                    f'Ensure <entry kind="{expected_kind}" id="..." .../> uses a '
                    "valid ID (e.g., PY1xx / PY10x)."
                ),
            )
            continue
        if not label or not desc or not rel_path:
            _log_error(
                errors,
                where=str(index_xml),
                problem=f"Missing label/desc/path for {expected_kind} '{entry_id}'.",
                fix="Add label, desc, and path attributes on the <entry> element.",
            )
            continue
        if entry_id in entries:
            _log_error(
                errors,
                where=str(index_xml),
                problem=f"Duplicate {expected_kind} entry '{entry_id}'.",
                fix="Remove duplicates; each ID must be defined exactly once.",
            )
            continue

        target = (index_xml.parent / rel_path).resolve()
        if not target.exists():
            _log_error(
                errors,
                where=str(index_xml),
                problem=(
                    f"Referenced path does not exist for {expected_kind} '{entry_id}': "
                    f"'{rel_path}'."
                ),
                fix=(
                    "Create the referenced file or update the path to an existing file."
                ),
            )
            continue

        entries[entry_id] = Meta(
            entry_id=entry_id, label=label, desc=desc, target_path=target
        )

    return entries


def _iter_rules_from_xml(language_root: Path, *, errors: list[str]) -> list[Rule]:
    rules: list[Rule] = []
    seen: set[str] = set()
    for path in sorted(language_root.rglob("*.xml")):
        if path.name in {"index.xml", "index-catalog.xml"}:
            continue
        # Skip the generator outputs in nested folders if any
        if path.name.startswith("index-catalog"):
            continue
        try:
            tree = ET.parse(path)  # noqa: S314
        except (ET.ParseError, OSError) as e:
            _log_error(
                errors,
                where=str(path),
                problem=f"Invalid XML: {e}",
                fix="Fix XML well-formedness (unclosed tags, invalid characters).",
            )
            continue
        root = tree.getroot()
        for rule_el in root.findall(".//rule"):
            rule_id = (rule_el.get("id") or "").strip()
            desc = (rule_el.findtext("desc") or "").strip()
            if not rule_id or not RULE_ID_RE.match(rule_id):
                _log_error(
                    errors,
                    where=str(path),
                    problem=f"Missing/invalid rule id on <rule>: '{rule_id}'.",
                    fix="Ensure each <rule> has id like 'PY200-PACKAGE-INIT'.",
                )
                continue
            if not desc:
                _log_error(
                    errors,
                    where=str(path),
                    problem=f"Missing rule desc for '{rule_id}'.",
                    fix=(
                        "Add a non-empty <desc>...</desc> element under the <rule> "
                        "element."
                    ),
                )
                continue
            if rule_id in seen:
                _log_error(
                    errors,
                    where=str(path),
                    problem=f"Duplicate rule id '{rule_id}'.",
                    fix="Ensure rule IDs are unique across the language pack.",
                )
                continue
            seen.add(rule_id)

            rel_path = path.relative_to(language_root).as_posix()
            rules.append(Rule(rule_id=rule_id, desc=desc, rel_path=rel_path))
    return rules


def _render_catalog_xml(  # noqa: C901, PLR0913
    *,
    language: str,
    source_root: str,
    entrypoint_rel: str,
    rules: list[Rule],
    hundreds_meta: dict[str, Meta],
    tens_meta_by_hundreds: dict[str, dict[str, Meta]],
) -> str:
    updated = "1970-01-01"

    def try_updated_attr(path: Path) -> str:
        try:
            root = ET.parse(path).getroot()  # noqa: S314
        except (ET.ParseError, OSError):
            return ""
        return (root.get("updated") or "").strip()

    # Best-effort: use the max updated value from inputs (lexicographic works for
    # YYYY-MM-DD).
    for p in {h.target_path for h in hundreds_meta.values()}:
        updated = max(updated, try_updated_attr(p))

    root = ET.Element(
        "catalog",
        {
            "id": f"CTX-CODING-STANDARDS-{language.upper()}-INDEX-CATALOG",
            "title": "index catalog",
            "kind": "manifest",
            "version": "2",
            "updated": updated or "1970-01-01",
            "status": "active",
            "language": language,
            "sourceRoot": source_root,
            "entrypoint": entrypoint_rel,
        },
    )

    def section_desc(kind: str) -> str:
        return (
            "Normative rules to follow."
            if kind == "guidelines"
            else "Patterns to avoid."
        )

    rules_by_kind: dict[str, list[Rule]] = {"guidelines": [], "antipatterns": []}
    for r in rules:
        prefix, _num = _parse_rule_id(r.rule_id)
        rules_by_kind[
            "guidelines" if _is_guideline_prefix(prefix) else "antipatterns"
        ].append(r)

    for kind in ("guidelines", "antipatterns"):
        kind_rules = rules_by_kind[kind]
        if not kind_rules:
            continue
        section_el = ET.SubElement(
            root,
            "section",
            {
                "kind": kind,
                "label": "Guidelines" if kind == "guidelines" else "Anti-Patterns",
                "desc": section_desc(kind),
            },
        )

        by_hundreds: dict[str, list[Rule]] = defaultdict(list)
        for r in kind_rules:
            prefix, num = _parse_rule_id(r.rule_id)
            by_hundreds[_hundreds_id(prefix, num)].append(r)

        for hid in sorted(by_hundreds.keys()):
            hmeta = hundreds_meta[hid]
            hundreds_el = ET.SubElement(
                section_el,
                "hundreds",
                {"id": hid, "label": hmeta.label, "desc": hmeta.desc},
            )

            tens_meta = tens_meta_by_hundreds[hid]
            by_file: dict[str, list[Rule]] = defaultdict(list)
            for r in by_hundreds[hid]:
                by_file[r.rel_path].append(r)

            for file_path in sorted(by_file.keys()):
                file_el = ET.SubElement(hundreds_el, "file")
                ET.SubElement(file_el, "doc_ref", {"path": file_path})
                rules_by_tens: dict[str, list[Rule]] = defaultdict(list)
                for r in by_file[file_path]:
                    pfx, num = _parse_rule_id(r.rule_id)
                    rules_by_tens[_tens_id(pfx, num)].append(r)

                for tid in sorted(rules_by_tens.keys()):
                    tmeta = tens_meta[tid]
                    tens_el = ET.SubElement(
                        file_el,
                        "tens",
                        {"id": tid, "label": tmeta.label, "desc": tmeta.desc},
                    )
                    for r in sorted(rules_by_tens[tid], key=lambda x: x.rule_id):
                        ET.SubElement(
                            tens_el,
                            "rule",
                            {"id": r.rule_id, "desc": r.desc},
                        )

    return canonical_xml_string(root)


def main(argv: list[str]) -> int:  # noqa: C901, PLR0912, PLR0915
    """Generate (or check) `index-catalog.xml` outputs for all languages."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="Fail if outputs are out of date."
    )
    args = parser.parse_args(argv)

    if not CODING_STANDARDS_DIR.exists():
        sys.stderr.write(f"coding standards dir not found: {CODING_STANDARDS_DIR}\n")
        return 2

    errors: list[str] = []
    outputs: dict[Path, str] = {}

    for language_root in sorted(CODING_STANDARDS_DIR.iterdir()):
        if not language_root.is_dir():
            continue
        if language_root.name.startswith("_"):
            continue

        language_errors_before = len(errors)
        index_xml = language_root / "index.xml"
        if not index_xml.exists():
            # Skip empty language folders, but fail if rules exist.
            if any(language_root.rglob("*.xml")):
                _log_error(
                    errors,
                    where=str(language_root),
                    problem="Missing required language metadata index.xml.",
                    fix=(
                        f'Create {index_xml} with <entry kind="hundreds" .../> '
                        "definitions."
                    ),
                )
            continue

        rules = _iter_rules_from_xml(language_root, errors=errors)
        if not rules:
            continue

        expected_hundreds: set[str] = set()
        expected_tens_by_h: dict[str, set[str]] = defaultdict(set)
        for r in rules:
            prefix, num = _parse_rule_id(r.rule_id)
            hid = _hundreds_id(prefix, num)
            tid = _tens_id(prefix, num)
            expected_hundreds.add(hid)
            expected_tens_by_h[hid].add(tid)

        hundreds_meta = _parse_index_entries(
            index_xml=index_xml,
            errors=errors,
            expected_kind="hundreds",
            id_re=HUNDREDS_ID_RE,
        )

        for hid in sorted(expected_hundreds):
            if hid not in hundreds_meta:
                _log_error(
                    errors,
                    where=str(index_xml),
                    problem=f"Missing hundreds metadata for '{hid}'.",
                    fix=(
                        f'Add <entry kind="hundreds" id="{hid}" label="..." '
                        'desc="..." path="./.../index.xml"/>.'
                    ),
                )

        tens_meta_by_hundreds: dict[str, dict[str, Meta]] = {}
        for hid in sorted(expected_hundreds):
            hmeta = hundreds_meta.get(hid)
            if hmeta is None:
                continue
            hundreds_index_xml = hmeta.target_path
            if hundreds_index_xml.name != "index.xml":
                _log_error(
                    errors,
                    where=str(index_xml),
                    problem=(
                        f"Hundreds entry '{hid}' must reference an index.xml file "
                        f"(got {hundreds_index_xml})."
                    ),
                    fix=(
                        "Update the path=... to point at a hundreds bucket index.xml "
                        "file."
                    ),
                )
                continue
            tens_meta = _parse_index_entries(
                index_xml=hundreds_index_xml,
                errors=errors,
                expected_kind="tens",
                id_re=TENS_ID_RE,
            )

            for tid in sorted(expected_tens_by_h[hid]):
                if tid not in tens_meta:
                    _log_error(
                        errors,
                        where=str(hundreds_index_xml),
                        problem=(
                            f"Missing tens metadata for '{tid}' (required by rules in "
                            f"{hid})."
                        ),
                        fix=(
                            f'Add <entry kind="tens" id="{tid}" label="..." desc="..." '
                            'path="./..."/>.'
                        ),
                    )

            tens_meta_by_hundreds[hid] = tens_meta

        if len(errors) != language_errors_before:
            continue

        out_path = language_root / "index-catalog.xml"
        xml = _render_catalog_xml(
            language=language_root.name,
            source_root=f".claude/context/coding-standards/{language_root.name}",
            entrypoint_rel=_posix_relpath(
                CODING_STANDARDS_DIR.parent / "coding-standards.md", language_root
            ),
            rules=rules,
            hundreds_meta=hundreds_meta,
            tens_meta_by_hundreds=tens_meta_by_hundreds,
        )
        outputs[out_path] = xml

    if errors:
        sys.stderr.write("\n".join(errors) + "\n")
        return 1

    for out_path, content in outputs.items():
        _write_if_changed(out_path, content, check=args.check)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
