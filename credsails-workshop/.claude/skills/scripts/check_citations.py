#!/usr/bin/env python3
"""check_citations.py — verify every domain-skill `## Sources` citation against the report.

This is the MANDATORY integrity guardrail for the CRISIL "domain" skill category.
Those skills carry domain content directly (no MCP backstop), so the only thing
keeping their citations honest is: every quote must still resolve, verbatim, in
the source report under the section it claims.

For each `<skill>/SKILL.md` under `.claude/skills/` that has a `## Sources`
block, this parses the citations and checks, for each one:

  1. the `section_path` leaf heading still exists in the report, and
  2. the `quote`, after markdown/whitespace normalization, is a substring of
     that section's text.

Normalization strips mermaid `<br/>` line-breaks and `:::class` suffixes and
collapses whitespace — because most report facts live inside mermaid-node labels.

The whole-report SHA is compared to a single pinned constant: a mismatch prints
ONE informational "report changed — re-validate" notice (not a per-skill
failure). Quote-resolution is the real drift signal and the only thing that
fails the run.

Exit code: 0 if every citation resolves; 1 if any quote/section is unresolved;
2 on setup errors (report not found, etc.).

Usage:
    python check_citations.py                 # check all domain skills
    python check_citations.py --emit-index    # also (re)generate references/REPORT_SECTIONS.md
    python check_citations.py --report PATH    # override report location
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Pinned provenance stamp: sha256 of CRISIL_CovIQ_CredSails_FULL_REPORT.md as
# validated when these skills were authored. A mismatch is informational only.
REPORT_SHA256 = "8232a0ba4febdf881a483bed101dbe6aa12d817da1bf997553185a0d79dbea5e"

SCRIPTS_DIR = Path(__file__).resolve().parent          # .../.claude/skills/scripts
SKILLS_DIR = SCRIPTS_DIR.parent                        # .../.claude/skills
# Report lives in the workspace knowledge-base/, one level above the harness-mcp repo.
DEFAULT_REPORT = SCRIPTS_DIR.parents[3] / "knowledge-base" / "CRISIL_CovIQ_CredSails_FULL_REPORT.md"
INDEX_PATH = SKILLS_DIR / "references" / "REPORT_SECTIONS.md"

PATH_SEP = "›"  # › breadcrumb separator (also accepts plain '>')


def normalize(s: str) -> str:
    """Collapse a chunk of report/quote text so verbatim quotes match even when
    they sit inside mermaid nodes or carry markdown emphasis."""
    s = s.replace("<br/>", " ").replace("<br>", " ")
    s = re.sub(r":::[A-Za-z0-9_-]+", " ", s)  # mermaid class suffixes
    s = s.replace("*", "").replace("`", "")    # bold/italic/code markers
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def parse_headings(lines: List[str]) -> List[Tuple[int, str, int]]:
    """Return [(level, normalized_title, line_index), ...] for every ATX heading."""
    out: List[Tuple[int, str, int]] = []
    in_fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if m:
            out.append((len(m.group(1)), normalize(m.group(2)), i))
    return out


def section_text(lines: List[str], headings: List[Tuple[int, str, int]], leaf: str) -> Optional[str]:
    """Normalized text of the section whose leaf heading == `leaf`, spanning until
    the next heading of the same or higher level (so child subsections are included)."""
    leaf_n = normalize(leaf)
    for idx, (level, title, line_no) in enumerate(headings):
        if title == leaf_n:
            end = len(lines)
            for level2, _t2, line_no2 in headings[idx + 1:]:
                if level2 <= level:
                    end = line_no2
                    break
            return normalize("\n".join(lines[line_no:end]))
    return None


def parse_sources(skill_md: str) -> List[Tuple[str, str]]:
    """Extract [(section_path, quote), ...] from a SKILL.md `## Sources` block."""
    m = re.search(r"^##\s+Sources\s*$(.*?)(^##\s|\Z)", skill_md, re.MULTILINE | re.DOTALL)
    if not m:
        return []
    block = m.group(1)
    cites: List[Tuple[str, str]] = []
    current_path: Optional[str] = None
    for line in block.splitlines():
        mp = re.match(r"^\s*-\s*section_path:\s*(.+?)\s*$", line)
        if mp:
            current_path = mp.group(1)
            continue
        mq = re.match(r"^\s*quote:\s*(.+?)\s*$", line)
        if mq and current_path is not None:
            q = mq.group(1).strip()
            if len(q) >= 2 and q[0] == '"' and q[-1] == '"':
                q = q[1:-1]
            cites.append((current_path, q))
            current_path = None
    return cites


def leaf_of(section_path: str) -> str:
    parts = re.split(r"[" + PATH_SEP + r">]", section_path)
    return parts[-1].strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="Path to the source report.")
    ap.add_argument("--emit-index", action="store_true", help="(Re)generate references/REPORT_SECTIONS.md.")
    args = ap.parse_args()

    if not args.report.exists():
        print(f"ERROR: report not found: {args.report}", file=sys.stderr)
        return 2

    report_bytes = args.report.read_bytes()
    actual_sha = hashlib.sha256(report_bytes).hexdigest()
    if actual_sha != REPORT_SHA256:
        print(
            f"NOTICE: report SHA changed since citations were pinned "
            f"(pinned {REPORT_SHA256[:12]}…, now {actual_sha[:12]}…). "
            f"Re-validate quotes and update REPORT_SHA256.",
        )

    lines = report_bytes.decode("utf-8").splitlines()
    headings = parse_headings(lines)

    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    total = 0
    errors: List[str] = []
    index: Dict[str, List[str]] = {}

    for sf in skill_files:
        text = sf.read_text(encoding="utf-8")
        cites = parse_sources(text)
        if not cites:
            continue  # role/language skills have no ## Sources — skip
        skill = sf.parent.name
        index[skill] = []
        for section_path, quote in cites:
            total += 1
            leaf = leaf_of(section_path)
            index[skill].append(section_path)
            sect = section_text(lines, headings, leaf)
            if sect is None:
                errors.append(f"{skill}: section not found — {leaf!r} (path: {section_path})")
                continue
            if normalize(quote) not in sect:
                errors.append(f"{skill}: quote not under {leaf!r} — {quote!r}")

    for e in errors:
        print(f"FAIL  {e}", file=sys.stderr)

    print(f"\nChecked {total} citations across {len(index)} domain skills: "
          f"{total - len(errors)} ok, {len(errors)} failed.")

    if args.emit_index:
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        out = ["# Report citation index (generated — do not edit by hand)",
               "",
               f"Generated by `scripts/check_citations.py --emit-index` from "
               f"`{args.report.name}` (sha256 `{actual_sha[:12]}…`).",
               "",
               "Maps each domain skill to the report sections it cites.",
               ""]
        for skill in sorted(index):
            out.append(f"## {skill}")
            for sp in index[skill]:
                out.append(f"- {sp}")
            out.append("")
        INDEX_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"Wrote {INDEX_PATH.relative_to(SKILLS_DIR)}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
