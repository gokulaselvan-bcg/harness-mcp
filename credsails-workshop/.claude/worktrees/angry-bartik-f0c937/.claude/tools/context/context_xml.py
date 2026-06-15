"""
Context XML canonicalization utilities.

These helpers implement the repository's deterministic XML formatting rules for
`.claude/context/**/*.xml`, including:
- Stable attribute ordering (metadata first)
- Deterministic child ordering where safe (e.g., rules/entries sorted by `id`)
- 2-space indentation
- `<code>` stored as CDATA (content preserved verbatim)
- Single-line leaf elements keep the closing tag on the same line

Consumers:
- `.claude/tools/context/validate_context.py` (validation + optional auto-fix)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path
    from xml.etree import ElementTree as ET

RULE_ID_RE = re.compile(r"\b[A-Z]{1,2}\d{3}-[A-Z0-9-]+\b")

CDATA_INVALID_MESSAGE = "<code> content contains ']]>' which is not allowed in CDATA"


class InvalidCdataError(ValueError):
    """Raised when CDATA text contains an invalid sequence."""

    def __init__(self) -> None:
        """Create an invalid-CDATA error."""
        super().__init__(CDATA_INVALID_MESSAGE)


ROOT_ATTR_ORDER = ("id", "title", "kind", "version", "updated", "status", "path")


@dataclass(frozen=True)
class CanonicalizeResult:
    """Result of an XML canonicalization operation."""

    xml: str
    changed: bool


def is_rule_id(s: str) -> bool:
    """Return True if `s` matches the rule-id format (for example, `PY123-FOO`)."""
    return bool(re.fullmatch(r"[A-Z]{1,2}\d{3}-[A-Z0-9-]+", s))


def _escape_attr(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _escape_text(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _format_attrs(attrib: dict[str, str]) -> str:
    if not attrib:
        return ""
    ordered = [k for k in ROOT_ATTR_ORDER if k in attrib]
    ordered_set = set(ordered)
    ordered.extend(k for k in sorted(attrib.keys()) if k not in ordered_set)
    parts = [f' {k}="{_escape_attr(attrib[k])}"' for k in ordered]
    return "".join(parts)


def _has_mixed_content(elem: ET.Element) -> bool:
    if elem.text and elem.text.strip():
        return True
    return any(child.tail and child.tail.strip() for child in list(elem))


def _serialize(elem: ET.Element, *, indent: str, level: int) -> str:  # noqa: C901
    pad = indent * level
    attrs = _format_attrs(elem.attrib)
    children = list(elem)

    if elem.tag == "code":
        text = elem.text or ""
        if "]]>" in text:
            raise InvalidCdataError
        return f"{pad}<{elem.tag}{attrs}><![CDATA[{text}]]></{elem.tag}>"

    if not children:
        text = elem.text or ""
        # If this is a single-line leaf node that ends with a trailing newline,
        # keep the closing tag on the same line by stripping only trailing "\n".
        if text.endswith("\n"):
            trimmed = text.rstrip("\n")
            if trimmed and "\n" not in trimmed:
                text = trimmed
        if text:
            return f"{pad}<{elem.tag}{attrs}>{_escape_text(text)}</{elem.tag}>"
        return f"{pad}<{elem.tag}{attrs}/>"

    if _has_mixed_content(elem):
        # Preserve content; do not inject indentation/newlines inside.
        s = [f"{pad}<{elem.tag}{attrs}>"]
        if elem.text:
            s.append(_escape_text(elem.text))
        for child in children:
            s.append(_serialize(child, indent=indent, level=0))
            if child.tail:
                s.append(_escape_text(child.tail))
        s.append(f"</{elem.tag}>")
        return "".join(s)

    # Block formatting.
    lines: list[str] = [f"{pad}<{elem.tag}{attrs}>"]
    if elem.text and elem.text.strip():
        lines.append(f"{pad}{indent}{_escape_text(elem.text.strip())}")
    lines.extend(
        _serialize(child, indent=indent, level=level + 1) for child in children
    )
    lines.append(f"{pad}</{elem.tag}>")
    return "\n".join(lines)


def _reorder_attrib(elem: ET.Element) -> None:
    if not elem.attrib:
        return
    attrib = dict(elem.attrib)
    elem.attrib.clear()
    for k in ROOT_ATTR_ORDER:
        if k in attrib:
            elem.set(k, attrib[k])
    for k in sorted(attrib.keys()):
        if k not in elem.attrib:
            elem.set(k, attrib[k])


def _sort_children(elem: ET.Element) -> None:  # noqa: C901
    """
    Apply deterministic ordering where it is safe and expected.
    """
    children = list(elem)
    if not children:
        return

    # Sort rule lists.
    if elem.tag == "rules":
        rules = [c for c in children if c.tag == "rule" and c.get("id")]
        if len(rules) == len(children):
            elem[:] = sorted(children, key=lambda e: e.get("id", ""))
            return

    # Sort manifest entries.
    if elem.tag == "section":
        entries = [c for c in children if c.tag == "entry" and c.get("id")]
        if entries and len(entries) == len(children):
            elem[:] = sorted(children, key=lambda e: e.get("id", ""))
            return

    # Sort related refs.
    if elem.tag in {"related", "better"}:
        # Allow either:
        #  - a pure <ref/> list
        #  - <ref/><todo kind="unresolved-ref" target="..."/> pairs
        pairs: list[tuple[str, list[ET.Element]]] = []
        i = 0
        ok = True
        while i < len(children):
            c = children[i]
            if c.tag != "ref" or not c.get("id"):
                ok = False
                break
            rid = c.get("id", "")
            group = [c]
            if i + 1 < len(children):
                nxt = children[i + 1]
                if (
                    nxt.tag == "todo"
                    and (nxt.get("kind") or "") == "unresolved-ref"
                    and (nxt.get("target") or "") == rid
                ):
                    group.append(nxt)
                    i += 1
            pairs.append((rid, group))
            i += 1

        if ok and pairs:
            out: list[ET.Element] = []
            for _, group in sorted(pairs, key=lambda kv: kv[0]):
                out.extend(group)
            elem[:] = out
            return


def canonicalize_tree(root: ET.Element) -> ET.Element:
    """
    Canonicalize an ElementTree in-place and return the root.

    This normalizes:
    - attribute ordering
    - safe child ordering (rules/entries/refs)
    """
    for elem in root.iter():
        _reorder_attrib(elem)
        _sort_children(elem)
    return root


def canonical_xml_string(root: ET.Element, *, indent: str = "  ") -> str:
    """
    Serialize an XML root in the repository's canonical format.

    The output is always newline-terminated.
    """
    canonicalize_tree(root)
    return _serialize(root, indent=indent, level=0) + "\n"


def iter_xml_files(root: Path) -> Iterable[Path]:
    """Yield all `*.xml` files under `root`, sorted by path."""
    yield from sorted(root.rglob("*.xml"))
