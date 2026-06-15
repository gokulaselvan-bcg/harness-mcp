# Coding Standards - Entry Point

**Goal:** Make it easy for agents to discover and cite coding standards by ID.

This repository uses a split standards pack:

- **General (language-agnostic):** `./coding-standards/general/` (Y*/Z*)
- **Python-specific:** `./coding-standards/python/` (PY*/PZ*)
- **Java-specific:** `./coding-standards/java/` (JY*/JZ*)
- **TypeScript-specific:** `./coding-standards/typescript/` (TY*/TZ*)

Use these IDs:
- **General:** Y###-NAME (guidelines) and Z###-NAME (anti-patterns)
- **Python:** PY###-NAME and PZ###-NAME
- **Java:** JY###-NAME and JZ###-NAME
- **TypeScript:** TY###-NAME and TZ###-NAME

---

## Fast Discovery (Load These First)

If you need to see *all* standards in one go:

- General full catalog (Y*/Z*): `./coding-standards/general/index-catalog.xml`
- Python full catalog (PY*/PZ*): `./coding-standards/python/index-catalog.xml`
- Java full catalog (JY*/JZ*): `./coding-standards/java/index-catalog.xml`
- TypeScript full catalog (TY*/TZ*): `./coding-standards/typescript/index-catalog.xml`

Note: Language catalogs are **language-only** (PY/PZ, JY/JZ, or TY/TZ). For a complete pack
for a given language, load **General** + the **language** catalog.

---

## Structure (Metadata)

These XML index files are canonical for hundreds/tens descriptions used by the generator:

- General index: `./coding-standards/general/index.xml`
- Python index: `./coding-standards/python/index.xml`
- Java index: `./coding-standards/java/index.xml`
- TypeScript index: `./coding-standards/typescript/index.xml`

Structure guide: `./coding-standards/overview.md`
