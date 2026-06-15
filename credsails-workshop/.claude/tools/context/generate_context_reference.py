"""Generate human-readable Markdown reference pages from `.claude/context/*.xml`."""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTEXT_ROOT = REPO_ROOT / ".claude" / "context"
DEFAULT_OUTPUT_ROOT = (
    REPO_ROOT / "docs" / "src" / "content" / "docs" / "context" / "reference"
)
DEFAULT_BLOB_BASE = os.environ.get(
    "CONTEXT_REPO_BLOB_BASE",
    "https://github.com/bcgx-pi-genx-training/agentic-coding/blob/main",
)


@dataclass(frozen=True)
class SourceFile:
    """A source context XML file and its normalized repository-relative path."""

    abs_path: Path
    rel_posix: str


@dataclass(frozen=True)
class LinkTarget:
    """Represents a generated docs slug target."""

    slug: str
    output_path: Path


def _yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _normalize_spaces(value: str) -> str:
    return " ".join(value.split())


def _clean_text(value: str | None) -> str:
    return (value or "").strip()


def _humanize_context_text(value: str) -> str:
    """Remove schema-level taxonomy terms from rendered prose."""
    text = value
    replacements = (
        (r"\b[Tt]ens-level\b", "Group-level"),
        (r"\b[Tt]ens\b", "Groups"),
        (r"\b[Hh]undreds\b", "Categories"),
        (r"\bhundreds\b", "categories"),
        (r"\btens\b", "groups"),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text


def _title_from_filename(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").strip().title()


def _to_slug(rel_posix: str) -> str:
    stem = rel_posix.removesuffix(".xml")
    if stem == "index" or stem.endswith("/index"):
        stem = f"{stem}-xml"
    return f"context/reference/{stem}"


def _source_files(context_root: Path) -> list[SourceFile]:
    out: list[SourceFile] = []
    for path in sorted(context_root.rglob("*.xml")):
        rel_posix = path.relative_to(context_root).as_posix()
        out.append(SourceFile(abs_path=path, rel_posix=rel_posix))
    return out


def _paired_catalog_dirs(source_files: list[SourceFile]) -> set[str]:
    rels = {s.rel_posix for s in source_files}
    pairs: set[str] = set()
    for rel in rels:
        if not rel.endswith("/index-catalog.xml"):
            continue
        dir_rel = rel.removesuffix("/index-catalog.xml")
        if f"{dir_rel}/index.xml" in rels:
            pairs.add(dir_rel)
    return pairs


def _is_paired_index(rel_posix: str, paired_catalog_dirs: set[str]) -> bool:
    if rel_posix == "index.xml":
        return False
    if not rel_posix.endswith("/index.xml"):
        return False
    dir_rel = rel_posix.removesuffix("/index.xml")
    return dir_rel in paired_catalog_dirs


def _paired_catalog_rel(rel_posix: str) -> str:
    return f"{rel_posix.removesuffix('/index.xml')}/index-catalog.xml"


def _to_slug_with_pairs(rel_posix: str, paired_catalog_dirs: set[str]) -> str:
    if rel_posix.endswith("/index-catalog.xml"):
        dir_rel = rel_posix.removesuffix("/index-catalog.xml")
        if dir_rel in paired_catalog_dirs:
            return f"context/reference/{dir_rel}"
    if _is_paired_index(rel_posix, paired_catalog_dirs):
        return _to_slug_with_pairs(_paired_catalog_rel(rel_posix), paired_catalog_dirs)
    return _to_slug(rel_posix)


def _output_path(output_root: Path, rel_posix: str) -> Path:
    rel = rel_posix.removesuffix(".xml")
    if rel == "index" or rel.endswith("/index"):
        rel = f"{rel}-xml"
    return output_root / Path(f"{rel}.md")


def _output_path_with_pairs(
    output_root: Path, rel_posix: str, paired_catalog_dirs: set[str]
) -> Path:
    if rel_posix.endswith("/index-catalog.xml"):
        dir_rel = rel_posix.removesuffix("/index-catalog.xml")
        if dir_rel in paired_catalog_dirs:
            return output_root / dir_rel / "index.md"
    if _is_paired_index(rel_posix, paired_catalog_dirs):
        return _output_path_with_pairs(
            output_root, _paired_catalog_rel(rel_posix), paired_catalog_dirs
        )
    return _output_path(output_root, rel_posix)


def _blob_link(blob_base: str, rel_posix: str) -> str:
    return f"{blob_base.rstrip('/')}/.claude/context/{rel_posix}"


def _render_code_literal(value: str) -> str:
    return f"`{value.replace('`', '\\`')}`"


def _escape_html_text(value: str) -> str:
    return html.escape(value, quote=False)


def _escape_html_attr(value: str) -> str:
    return html.escape(value, quote=True)


def _escape_html_table_text(value: str) -> str:
    # Avoid Markdown table cell splits on pipes while keeping readable labels.
    return _escape_html_text(value).replace("|", "&#124;")


def _rule_anchor(rule_id: str) -> str:
    return rule_id.lower()


def _render_rule_link(
    rule_id: str, rule_id_to_slug: dict[str, str], unresolved_ids: set[str]
) -> str:
    slug = rule_id_to_slug.get(rule_id)
    if slug:
        return f"[{rule_id}](/{slug}#{_rule_anchor(rule_id)})"
    unresolved_ids.add(rule_id)
    return f"`{rule_id}`"


def _render_doc_ref_link(
    *,
    source_file: SourceFile,
    doc_ref_path: str,
    context_root: Path,
    source_to_target: dict[str, LinkTarget],
    blob_base: str,
) -> str:
    resolved = (source_file.abs_path.parent / doc_ref_path).resolve()
    if not resolved.exists():
        return _render_code_literal(doc_ref_path)
    try:
        rel = resolved.relative_to(context_root).as_posix()
    except ValueError:
        return _render_code_literal(doc_ref_path)
    target = source_to_target.get(rel)
    if target:
        return (
            f'<a href="/{_escape_html_attr(target.slug)}">'
            f"{_escape_html_text(doc_ref_path)}</a>"
        )
    return (
        f'<a href="{_escape_html_attr(_blob_link(blob_base, rel))}" '
        f'target="_blank" rel="noopener noreferrer">'
        f"{_escape_html_text(doc_ref_path)}</a>"
    )


def _render_doc_ref_raw_link(
    *,
    source_file: SourceFile,
    doc_ref_path: str,
    context_root: Path,
    blob_base: str,
) -> str:
    resolved = (source_file.abs_path.parent / doc_ref_path).resolve()
    if not resolved.exists():
        return _render_code_literal(doc_ref_path)
    try:
        rel = resolved.relative_to(context_root).as_posix()
    except ValueError:
        return _render_code_literal(doc_ref_path)
    return (
        f'<a href="{_escape_html_attr(_blob_link(blob_base, rel))}" '
        f'target="_blank" rel="noopener noreferrer">'
        f"{_escape_html_text(doc_ref_path)}</a>"
    )


def _display_kind(kind: str) -> str:
    kind_lower = kind.lower()
    if kind_lower in {"hundreds", "tens"}:
        return ""
    return kind


def _escape_table_cell(value: str) -> str:
    escaped = _escape_html_text(value)
    text = escaped.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>")
    return text.replace("|", "&#124;")


def _humanize_heading(heading: str) -> str:
    lowered = heading.strip().lower()
    if lowered == "tens":
        return "Groups"
    if lowered == "hundreds":
        return "Categories"
    return heading


def _collect_text_parts(text: str) -> list[str]:
    cleaned = text.strip()
    if not cleaned:
        return []
    lines = [ln.rstrip() for ln in cleaned.splitlines()]
    if len(lines) > 1 and all(line.startswith("- ") for line in lines if line):
        return [*(_escape_html_text(line) for line in lines), ""]
    return [_escape_html_text(cleaned), ""]


def _code_fence_lines(code_text: str, language: str) -> tuple[str, str]:
    runs = re.findall(r"`+", code_text)
    longest_run = max((len(run) for run in runs), default=0)
    fence = "`" * max(3, longest_run + 1)
    return f"{fence}{language}", fence


def _render_mixed_block(
    node: ET.Element,
    *,
    rule_id_to_slug: dict[str, str],
    unresolved_ids: set[str],
) -> list[str]:
    lines: list[str] = []
    inline: list[str] = []

    def flush_inline() -> None:
        text = "".join(inline)
        inline.clear()
        lines.extend(_collect_text_parts(text))

    if node.text:
        inline.append(node.text)

    for child in list(node):
        tag = child.tag
        if tag == "ref":
            inline.append(
                _render_rule_link(child.get("id", ""), rule_id_to_slug, unresolved_ids)
            )
        elif tag == "code":
            flush_inline()
            lang = _clean_text(child.get("lang")) or "text"
            code_text = (child.text or "").rstrip("\n")
            open_fence, close_fence = _code_fence_lines(code_text, lang)
            lines.append(open_fence)
            lines.append(code_text)
            lines.append(close_fence)
            lines.append("")
        elif tag == "todo":
            flush_inline()
            kind = _clean_text(child.get("kind")) or "unknown"
            target = _clean_text(child.get("target")) or "unknown"
            body = _clean_text(child.text)
            suffix = f" — {body}" if body else ""
            lines.append(f"> [!WARNING] TODO kind=`{kind}` target=`{target}`{suffix}")
            lines.append("")
        else:
            flush_inline()
            child_text = _clean_text("".join(child.itertext()))
            if child_text:
                lines.extend(_collect_text_parts(child_text))
        if child.tail:
            inline.append(child.tail)

    flush_inline()
    while lines and not lines[-1]:
        lines.pop()
    return lines


def _render_examples(
    examples: ET.Element,
    *,
    rule_id_to_slug: dict[str, str],
    unresolved_ids: set[str],
    heading_level: int = 3,
) -> list[str]:
    nodes = examples.findall("example")
    if not nodes:
        return []

    heading_prefix = "#" * heading_level
    subheading_prefix = "#" * (heading_level + 1)
    lines: list[str] = []
    if len(nodes) == 1:
        kind = _clean_text(nodes[0].get("kind")).lower()
        label = f"{kind.title()} Example" if kind in {"good", "bad"} else "Example"
        lines.extend([f"{heading_prefix} {label}", ""])
        lines.extend(
            _render_mixed_block(
                nodes[0], rule_id_to_slug=rule_id_to_slug, unresolved_ids=unresolved_ids
            )
        )
        return lines

    lines.extend([f"{heading_prefix} Examples", ""])
    counts: dict[str, int] = {}
    for node in nodes:
        kind = _clean_text(node.get("kind")).lower() or "example"
        counts[kind] = counts.get(kind, 0) + 1
        label = f"{kind.title()} Example {counts[kind]}"
        lines.extend([f"{subheading_prefix} {label}", ""])
        lines.extend(
            _render_mixed_block(
                node, rule_id_to_slug=rule_id_to_slug, unresolved_ids=unresolved_ids
            )
        )
        lines.append("")
    while lines and not lines[-1]:
        lines.pop()
    return lines


def _compact_text(lines: list[str]) -> str:
    return _normalize_spaces(" ".join(line.strip() for line in lines if line.strip()))


def _is_compactable(lines: list[str]) -> bool:
    max_lines = 2
    if not lines:
        return False
    if len(lines) > max_lines:
        return False
    disallowed_prefixes = ("```", "- ", "> ")
    return not any(line.startswith(disallowed_prefixes) for line in lines)


def _first_sentence(value: str) -> str:
    text = _normalize_spaces(value)
    if not text:
        return ""
    match = re.search(r"(?<!\.)[.!?](?!\.)(?:\s|$)", text)
    if not match:
        return text
    return text[: match.end()].strip()


def _truncate(value: str, max_len: int = 140) -> str:
    text = _normalize_spaces(value)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def _render_rules(  # noqa: C901, PLR0912, PLR0915
    root: ET.Element,
    *,
    rule_id_to_slug: dict[str, str],
    unresolved_ids: set[str],
) -> list[str]:
    lines: list[str] = []
    rule_nodes = root.findall("./rule")
    multi_rule = len(rule_nodes) > 1

    if multi_rule:
        lines.extend(
            [
                "## Rule Catalog",
                "",
                "| Rule | Summary |",
                "| --- | --- |",
            ]
        )
        for rule in rule_nodes:
            rid = _clean_text(rule.get("id")) or "UNKNOWN-RULE"
            desc = _first_sentence(_clean_text(rule.findtext("desc")))
            summary = _escape_table_cell(_truncate(desc)) if desc else "-"
            lines.append(f"| [{rid}](#{_rule_anchor(rid)}) | {summary} |")
        lines.extend(["", "## Rule Details", ""])

    fields = {
        "better": "Better",
        "why_bad": "Why This Is Problematic",
        "when_to_use": "When To Use",
        "exceptions": "Exceptions",
        "rationale": "Rationale",
        "tool_support": "Tool Support",
    }

    for idx, rule in enumerate(rule_nodes):
        rid = _clean_text(rule.get("id")) or "UNKNOWN-RULE"
        lines.extend([f'<a id="{_rule_anchor(rid)}"></a>', "", f"### {rid}", ""])

        desc = _clean_text(rule.findtext("desc"))
        if desc:
            lines.extend([_escape_html_text(desc), ""])

        for key, title in fields.items():
            node = rule.find(key)
            if node is None:
                continue
            rendered = _render_mixed_block(
                node, rule_id_to_slug=rule_id_to_slug, unresolved_ids=unresolved_ids
            )
            if multi_rule and _is_compactable(rendered):
                lines.append(f"- **{title}:** {_compact_text(rendered)}")
                continue
            heading = "####" if multi_rule else "###"
            if lines and lines[-1]:
                lines.append("")
            lines.extend([f"{heading} {title}", ""])
            lines.extend(rendered)
            lines.append("")

        examples = rule.find("examples")
        if examples is not None:
            nodes = examples.findall("example")
            if multi_rule and len(nodes) == 1:
                kind = _clean_text(nodes[0].get("kind")).lower()
                label = (
                    f"{kind.title()} Example" if kind in {"good", "bad"} else "Example"
                )
                rendered = _render_mixed_block(
                    nodes[0],
                    rule_id_to_slug=rule_id_to_slug,
                    unresolved_ids=unresolved_ids,
                )
                if _is_compactable(rendered):
                    lines.extend([f"- **{label}:** {_compact_text(rendered)}", ""])
                else:
                    if lines and lines[-1]:
                        lines.append("")
                    lines.extend(
                        _render_examples(
                            examples,
                            rule_id_to_slug=rule_id_to_slug,
                            unresolved_ids=unresolved_ids,
                            heading_level=4,
                        )
                    )
                    lines.append("")
            else:
                if lines and lines[-1]:
                    lines.append("")
                lines.extend(
                    _render_examples(
                        examples,
                        rule_id_to_slug=rule_id_to_slug,
                        unresolved_ids=unresolved_ids,
                        heading_level=4 if multi_rule else 3,
                    )
                )
                lines.append("")

        related = [
            r.get("id", "") for r in rule.findall("./related/ref") if r.get("id")
        ]
        if related:
            if multi_rule:
                items = ", ".join(
                    _render_rule_link(rid, rule_id_to_slug, unresolved_ids)
                    for rid in related
                )
                lines.extend([f"- **Related:** {items}", ""])
            else:
                lines.extend(["### Related Rules", ""])
                lines.extend(
                    f"- {_render_rule_link(rid, rule_id_to_slug, unresolved_ids)}"
                    for rid in related
                )
                lines.append("")

        keywords = [kw.text.strip() for kw in rule.findall("./keywords/kw") if kw.text]
        if keywords:
            if multi_rule:
                lines.extend(
                    [f"- **Keywords:** {', '.join(f'`{kw}`' for kw in keywords)}", ""]
                )
            else:
                lines.extend(
                    ["### Keywords", "", ", ".join(f"`{kw}`" for kw in keywords), ""]
                )

        note_nodes = rule.findall("./notes/note")
        if note_nodes:
            heading = "####" if multi_rule else "###"
            lines.extend([f"{heading} Notes", ""])
            for note in note_nodes:
                title = _escape_html_text(_clean_text(note.get("title")) or "Note")
                text = _escape_html_text(_normalize_spaces("".join(note.itertext())))
                lines.append(f"- **{title}:** {text}")
            lines.append("")

        todo_nodes = rule.findall("./todo")
        if todo_nodes:
            heading = "####" if multi_rule else "###"
            lines.extend([f"{heading} TODO", ""])
            for todo in todo_nodes:
                kind = _clean_text(todo.get("kind")) or "unknown"
                target = _clean_text(todo.get("target")) or "unknown"
                body = _clean_text(todo.text)
                suffix = f" — {body}" if body else ""
                lines.append(f"- kind=`{kind}` target=`{target}`{suffix}")
            lines.append("")

        if multi_rule:
            lines.extend(["[Back to Rule Catalog](#rule-catalog)", ""])
            if idx < len(rule_nodes) - 1:
                lines.extend(["---", ""])

    while lines and not lines[-1]:
        lines.pop()
    return lines


def _render_index(  # noqa: C901, PLR0912, PLR0915
    root: ET.Element,
    *,
    source_file: SourceFile,
    context_root: Path,
    source_to_target: dict[str, LinkTarget],
    blob_base: str,
) -> list[str]:
    lines: list[str] = []
    for section in root.findall("./section"):
        heading = (
            _clean_text(section.get("title"))
            or _clean_text(section.get("label"))
            or _clean_text(section.get("kind"))
            or "Section"
        )
        heading = _escape_html_text(_humanize_heading(heading))
        lines.extend([f"## {heading}", ""])

        sec_desc = _humanize_context_text(_clean_text(section.get("desc")))
        if sec_desc:
            lines.extend([_escape_html_text(sec_desc), ""])

        entries = section.findall("./entry")
        if not entries:
            sibling_xml = sorted(
                p
                for p in source_file.abs_path.parent.glob("*.xml")
                if p.name != source_file.abs_path.name
            )
            child_index_xml = sorted(source_file.abs_path.parent.glob("*/index.xml"))
            related = sibling_xml + [p for p in child_index_xml if p not in sibling_xml]
            if related:
                lines.append("Related context files:")
                lines.append("")
                for sibling in related:
                    rel = sibling.relative_to(context_root).as_posix()
                    target = source_to_target.get(rel)
                    label = sibling.name
                    if target is not None:
                        lines.append(f"- [{label}](/{target.slug})")
                    else:
                        lines.append(f"- `{label}`")
                lines.append("")
            else:
                lines.extend(["_No entries._", ""])
            continue

        lines.extend(
            [
                "| Item | Summary | Open |",
                "| --- | --- | --- |",
            ]
        )
        seen_open_targets: set[str] = set()
        for entry in entries:
            name = (
                _clean_text(entry.get("label"))
                or _clean_text(entry.get("title"))
                or _clean_text(entry.get("id"))
                or "Untitled"
            )
            desc = _normalize_spaces(
                _humanize_context_text(_clean_text(entry.get("desc")))
            )
            kind = _display_kind(_clean_text(entry.get("kind")))
            doc_ref = entry.find("doc_ref")
            doc_ref_path = (
                _clean_text(doc_ref.get("path")) if doc_ref is not None else ""
            )
            target = (
                _render_doc_ref_link(
                    source_file=source_file,
                    doc_ref_path=doc_ref_path,
                    context_root=context_root,
                    source_to_target=source_to_target,
                    blob_base=blob_base,
                )
                if doc_ref_path
                else ""
            )
            raw_target = (
                _render_doc_ref_raw_link(
                    source_file=source_file,
                    doc_ref_path=doc_ref_path,
                    context_root=context_root,
                    blob_base=blob_base,
                )
                if doc_ref_path
                else ""
            )
            safe_name = _escape_table_cell(name)
            item_label = safe_name
            open_target = ""
            if target.startswith('<a href="/') and target.endswith("</a>"):
                href_match = re.search(r'href="([^"]+)"', target)
                if href_match:
                    open_target = href_match.group(1)
            if open_target:
                item_label = (
                    f'<a href="{_escape_html_attr(open_target)}">'
                    f"{_escape_html_table_text(name)}</a>"
                )
            if doc_ref_path.endswith("index.xml") and open_target in seen_open_targets:
                continue
            summary_parts = [desc] if desc else []
            if kind:
                summary_parts.append(kind)
            summary = (
                _escape_table_cell(" — ".join(summary_parts)) if summary_parts else "-"
            )
            open_cell = raw_target or "-"
            lines.append(f"| {item_label} | {summary} | {open_cell} |")
            if open_target:
                seen_open_targets.add(open_target)
        lines.append("")

    while lines and not lines[-1]:
        lines.pop()
    return lines


def _render_catalog(  # noqa: C901, PLR0912, PLR0913, PLR0915
    root: ET.Element,
    *,
    source_file: SourceFile,
    context_root: Path,
    blob_base: str,
    rule_id_to_slug: dict[str, str],
    unresolved_ids: set[str],
) -> list[str]:
    def _catalog_anchor(*parts: str) -> str:
        raw = "-".join(_normalize_spaces(part).lower() for part in parts if part)
        slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
        return slug or "group"

    def _allocate_anchor(base: str, seen: dict[str, int]) -> str:
        count = seen.get(base, 0) + 1
        seen[base] = count
        if count == 1:
            return base
        return f"{base}-{count}"

    lines: list[str] = []
    anchor_counts: dict[str, int] = {}
    sections: list[dict[str, object]] = []

    for section in root.findall("./section"):
        section_label_raw = (
            _clean_text(section.get("label"))
            or _clean_text(section.get("title"))
            or _clean_text(section.get("kind"))
            or "Section"
        )
        section_label = _escape_html_text(section_label_raw)
        section_desc = _humanize_context_text(_clean_text(section.get("desc")))
        section_data: dict[str, object] = {
            "label": section_label,
            "desc": section_desc,
            "hundreds": [],
        }
        hundreds_data = section_data["hundreds"]
        if not isinstance(hundreds_data, list):
            continue

        for hundreds in section.findall("./hundreds"):
            hid = _clean_text(hundreds.get("id"))
            hlabel = _clean_text(hundreds.get("label"))
            hdesc = _humanize_context_text(_clean_text(hundreds.get("desc")))
            hundreds_title_raw = (
                f"{hid} — {hlabel}" if hid and hlabel else hlabel or hid or "Group"
            )
            hundreds_title = _escape_html_text(hundreds_title_raw)
            hundreds_entry: dict[str, object] = {
                "title": hundreds_title,
                "desc": _escape_html_text(hdesc) if hdesc else "",
                "groups": [],
            }
            groups_list = hundreds_entry["groups"]
            if not isinstance(groups_list, list):
                continue
            group_by_key: dict[str, dict[str, object]] = {}

            for file_node in hundreds.findall("./file"):
                doc_ref = file_node.find("doc_ref")
                doc_ref_path = (
                    _clean_text(doc_ref.get("path")) if doc_ref is not None else ""
                )
                source_link = (
                    _render_doc_ref_raw_link(
                        source_file=source_file,
                        doc_ref_path=doc_ref_path,
                        context_root=context_root,
                        blob_base=blob_base,
                    )
                    if doc_ref_path
                    else ""
                )
                for tens in file_node.findall("./tens"):
                    tid = _clean_text(tens.get("id"))
                    tlabel = _clean_text(tens.get("label"))
                    tdesc = _humanize_context_text(_clean_text(tens.get("desc")))
                    group_title_raw = (
                        f"{tid} — {tlabel}"
                        if tid and tlabel
                        else tlabel or tid or "Group"
                    )
                    group_title = _escape_html_text(group_title_raw)
                    group_key = f"{tid}|{tlabel}|{group_title_raw}".casefold()
                    group_entry = group_by_key.get(group_key)
                    if group_entry is None:
                        group_entry = {
                            "title": group_title,
                            "desc": _escape_html_text(tdesc) if tdesc else "",
                            "rows": [],
                            "anchor": "",
                        }
                        group_by_key[group_key] = group_entry
                        groups_list.append(group_entry)

                    rows = group_entry["rows"]
                    if not isinstance(rows, list):
                        continue
                    for rule in tens.findall("./rule"):
                        rid = _clean_text(rule.get("id")) or "UNKNOWN"
                        rdesc = _normalize_spaces(
                            _humanize_context_text(_clean_text(rule.get("desc")))
                        )
                        rlink = _render_rule_link(rid, rule_id_to_slug, unresolved_ids)
                        summary_parts = [rdesc] if rdesc else []
                        if tdesc:
                            summary_parts.append(tdesc)
                        summary = (
                            _escape_table_cell(" ".join(summary_parts))
                            if summary_parts
                            else "-"
                        )
                        rows.append((rlink, summary, source_link or "-"))

            for group in groups_list:
                if not isinstance(group, dict):
                    continue
                title_val = group.get("title")
                title = title_val if isinstance(title_val, str) else "Group"
                anchor_base = _catalog_anchor(
                    section_label_raw, hundreds_title_raw, title
                )
                group["anchor"] = _allocate_anchor(anchor_base, anchor_counts)
            hundreds_data.append(hundreds_entry)

        sections.append(section_data)

    if sections:
        # Keep this heading distinct from potential section labels named "Overview"
        # to avoid duplicate TOC anchor labels in Starlight navigation.
        lines.extend(["## Catalog Overview", ""])
        for section in sections:
            section_label = section["label"]
            if not isinstance(section_label, str):
                continue
            lines.append(f"- {section_label}")
            hundreds_entries = section.get("hundreds")
            if not isinstance(hundreds_entries, list):
                continue
            for hundreds_entry in hundreds_entries:
                if not isinstance(hundreds_entry, dict):
                    continue
                hundreds_title = hundreds_entry.get("title")
                if not isinstance(hundreds_title, str):
                    continue
                lines.append(f"  - {hundreds_title}")
                groups = hundreds_entry.get("groups")
                if not isinstance(groups, list):
                    continue
                for group in groups:
                    if not isinstance(group, dict):
                        continue
                    group_title = group.get("title")
                    group_anchor = group.get("anchor")
                    group_desc = group.get("desc")
                    if not isinstance(group_title, str) or not isinstance(
                        group_anchor, str
                    ):
                        continue
                    overview_line = f"    - [{group_title}](#{group_anchor})"
                    if isinstance(group_desc, str) and group_desc:
                        overview_line += f" — {group_desc}"
                    lines.append(overview_line)
        lines.append("")

    for section in sections:
        section_label = section["label"]
        if not isinstance(section_label, str):
            continue
        lines.extend([f"## {section_label}", ""])
        section_desc = section.get("desc")
        if isinstance(section_desc, str) and section_desc:
            lines.extend([section_desc, ""])

        hundreds_entries = section.get("hundreds")
        if not isinstance(hundreds_entries, list):
            continue
        for hundreds_entry in hundreds_entries:
            if not isinstance(hundreds_entry, dict):
                continue
            hundreds_title = hundreds_entry.get("title")
            if not isinstance(hundreds_title, str):
                continue
            lines.extend([f"### {hundreds_title}", ""])
            hundreds_desc = hundreds_entry.get("desc")
            if isinstance(hundreds_desc, str) and hundreds_desc:
                lines.extend([hundreds_desc, ""])

            groups = hundreds_entry.get("groups")
            if not isinstance(groups, list) or not groups:
                lines.extend(["_No catalog entries._", ""])
                continue

            for group in groups:
                if not isinstance(group, dict):
                    continue
                group_title = group.get("title")
                group_desc = group.get("desc")
                group_anchor = group.get("anchor")
                rows = group.get("rows")
                if (
                    not isinstance(group_title, str)
                    or not isinstance(group_anchor, str)
                    or not isinstance(rows, list)
                ):
                    continue
                lines.extend(
                    [f'<a id="{group_anchor}"></a>', "", f"#### {group_title}", ""]
                )
                if isinstance(group_desc, str) and group_desc:
                    lines.extend([group_desc, ""])
                if rows:
                    lines.extend(
                        [
                            "| Rule | Summary | Source |",
                            "| --- | --- | --- |",
                        ]
                    )
                    for rule, summary, source in rows:
                        lines.append(f"| {rule} | {summary} | {source} |")
                else:
                    lines.append("_No catalog entries._")
                lines.append("")

    while lines and not lines[-1]:
        lines.pop()
    return lines


def _description_for_xml(root: ET.Element, fallback_title: str) -> str:
    if root.tag == "rules":
        desc = _clean_text(root.findtext("./rule/desc"))
        if desc:
            return _normalize_spaces(desc)
    if root.tag == "index":
        section = root.find("./section")
        desc = _clean_text(section.get("desc")) if section is not None else ""
        if desc:
            return _normalize_spaces(_humanize_context_text(desc))
    return f"Human-readable reference for {fallback_title}."


def _render_xml_page(
    *,
    source_file: SourceFile,
    blob_base: str,
    context_root: Path,
    source_to_target: dict[str, LinkTarget],
    rule_id_to_slug: dict[str, str],
) -> tuple[str, set[str]]:
    try:
        root = ET.parse(source_file.abs_path).getroot()  # noqa: S314
    except ET.ParseError as exc:
        msg = f"Failed to parse XML file {source_file.rel_posix}: {exc}"
        raise ValueError(msg) from exc

    title = _clean_text(root.get("title")) or _title_from_filename(source_file.abs_path)
    desc = _description_for_xml(root, title)
    unresolved_ids: set[str] = set()

    lines: list[str] = [
        "---",
        f"title: {_yaml_quote(title)}",
        f"description: {_yaml_quote(desc)}",
        "---",
        "",
    ]

    if root.tag == "rules":
        lines.extend(
            _render_rules(
                root, rule_id_to_slug=rule_id_to_slug, unresolved_ids=unresolved_ids
            )
        )
    elif root.tag == "index":
        lines.extend(
            _render_index(
                root,
                source_file=source_file,
                context_root=context_root,
                source_to_target=source_to_target,
                blob_base=blob_base,
            )
        )
    elif root.tag == "catalog":
        lines.extend(
            _render_catalog(
                root,
                source_file=source_file,
                context_root=context_root,
                blob_base=blob_base,
                rule_id_to_slug=rule_id_to_slug,
                unresolved_ids=unresolved_ids,
            )
        )
    else:
        lines.extend(
            ["## Content", "", "_Unsupported XML root for specialized rendering._"]
        )

    lines.extend(
        [
            "",
            "---",
            "",
            (
                f'<a href="{_blob_link(blob_base, source_file.rel_posix)}" '
                f'target="_blank" '
                f'rel="noopener noreferrer">View raw XML source</a>'
            ),
        ]
    )

    return ("\n".join(lines).rstrip() + "\n"), unresolved_ids


def _build_rule_index(
    source_files: list[SourceFile],
) -> tuple[dict[str, str], list[str]]:
    rule_to_slug: dict[str, str] = {}
    errors: list[str] = []
    duplicates: dict[str, list[str]] = {}
    for source in source_files:
        try:
            root = ET.parse(source.abs_path).getroot()  # noqa: S314
        except ET.ParseError as exc:
            errors.append(f"Invalid XML at {source.rel_posix}: {exc}")
            continue
        if root.tag != "rules":
            continue
        for rule in root.findall("./rule[@id]"):
            rid = _clean_text(rule.get("id"))
            if not rid:
                continue
            slug = _to_slug(source.rel_posix)
            existing = rule_to_slug.get(rid)
            if existing and existing != slug:
                duplicates.setdefault(rid, [existing]).append(slug)
                continue
            rule_to_slug[rid] = slug

    for rid, slugs in sorted(duplicates.items()):
        uniq = sorted(set(slugs))
        errors.append(f"Duplicate rule id {rid}: {', '.join(uniq)}")
    return rule_to_slug, errors


def _write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _validate_output_root(*, context_root: Path, output_root: Path) -> str | None:
    """Return an error message when output_root is unsafe, otherwise None."""
    if output_root == REPO_ROOT:
        return "output root must not be repository root"
    if output_root == Path(output_root.anchor):
        return "output root must not be filesystem root"
    # Enforce repository containment only for in-repo context generation.
    try:
        context_root.relative_to(REPO_ROOT)
    except ValueError:
        return None
    try:
        output_root.relative_to(REPO_ROOT)
    except ValueError:
        return f"output root must be within repository: {output_root}"
    return None


def main(argv: list[str]) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--context-root", default=str(DEFAULT_CONTEXT_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--repo-blob-base", default=DEFAULT_BLOB_BASE)
    args = parser.parse_args(argv)

    context_root = Path(args.context_root).resolve()
    output_root = Path(args.output_root).resolve()
    blob_base = args.repo_blob_base

    if not context_root.exists():
        sys.stderr.write(f"context root not found: {context_root}\n")
        return 2
    output_root_error = _validate_output_root(
        context_root=context_root, output_root=output_root
    )
    if output_root_error:
        sys.stderr.write(f"{output_root_error}\n")
        return 2

    all_source_files = _source_files(context_root)
    if not all_source_files:
        sys.stderr.write(f"no supported context files found in: {context_root}\n")
        return 2
    paired_catalog_dirs = _paired_catalog_dirs(all_source_files)
    source_files = [
        source
        for source in all_source_files
        if not _is_paired_index(source.rel_posix, paired_catalog_dirs)
    ]

    source_to_target: dict[str, LinkTarget] = {}
    for source in all_source_files:
        source_to_target[source.rel_posix] = LinkTarget(
            slug=_to_slug_with_pairs(source.rel_posix, paired_catalog_dirs),
            output_path=_output_path_with_pairs(
                output_root, source.rel_posix, paired_catalog_dirs
            ),
        )

    rule_id_to_slug, build_errors = _build_rule_index(source_files)
    if build_errors:
        sys.stderr.write("\n".join(build_errors) + "\n")
        return 1

    shutil.rmtree(output_root, ignore_errors=True)

    unresolved_ref_ids: set[str] = set()
    for source in source_files:
        target = source_to_target[source.rel_posix].output_path
        content, unresolved = _render_xml_page(
            source_file=source,
            blob_base=blob_base,
            context_root=context_root,
            source_to_target=source_to_target,
            rule_id_to_slug=rule_id_to_slug,
        )
        unresolved_ref_ids.update(unresolved)
        _write_output(target, content)

    if unresolved_ref_ids:
        ids = ", ".join(sorted(unresolved_ref_ids))
        sys.stderr.write(
            f"warning: unresolved rule refs in generated markdown: {ids}\n"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
