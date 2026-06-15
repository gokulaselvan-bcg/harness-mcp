---
name: pull-ticket
description: Pull a user-specified Jira ticket into artifacts/tickets/{TICKET-ID}/ticket.md, create a ticket branch, and (optionally) transition status safely. Use when the user runs /pull-ticket PROJ-123 (or /pull-ticket 123).
---

# Pull Ticket Skill

Pulls a **user-specified** Jira ticket into agentic context and prepares the repo for implementation.

This skill intentionally does **not** include any logic to auto-select the "highest priority" ticket.

---

## Inputs

**Ticket ID/Key** (required):
- Full key: `PROJ-123`
- Short form: `123` (expand using the default Jira project key from `AGENTS.md`)

If no ticket ID is provided, **stop** and ask the user for a ticket key.

---

## Workflow

### 1. Verify Atlassian MCP

Invoke the **managing-jira** skill and apply **"Verify MCP Availability"**.

If MCP is unavailable or authentication fails, stop the workflow.

---

### 2. Resolve the ticket key

Parse the provided input:

- If input matches `[A-Z]+-[0-9]+` (e.g., `ABC-123`), use it as-is.
- If input is digits only (e.g., `123`), expand to `DEFAULT_PROJECT_KEY-123`, where
  `DEFAULT_PROJECT_KEY` comes from `AGENTS.md` (Default Variables → Jira Configuration).

If the default project key is missing or ambiguous, ask the user to provide the full ticket key (e.g.,
`PROJ-123`).

---

### 3. Fetch ticket details

Invoke the **managing-jira** skill and apply **"Get Ticket Details"** for the resolved key.

---

### 4. Detect blockers (inform-only)

If `issuelinks` indicate the ticket is blocked, surface the blockers in `ticket.md` and warn the user.
Do not switch tickets or reprioritize automatically.

---

### 5. Write `ticket.md`

Invoke the **managing-jira** skill and apply **"ticket.md Format"**.

- Write to: `artifacts/tickets/PROJ-123/ticket.md` (folder name matches resolved ticket key)
- Create `artifacts/tickets/PROJ-123/` if it does not exist
- Overwrite `ticket.md` for the same ticket if it already exists

---

### 6. Create ticket branch

Invoke the **managing-git** skill and apply **"Create Ticket Branch"**.

- Base branch: from `AGENTS.md` (Default Git Branch)
- Branch format: `ft/proj-123-ticket-name-slug` (prefix varies by work type: `ft/`, `rf/`, `doc/`,
  `test/`, `conf/`)
  - If unclear from the ticket, ask the user which prefix they want (default to `ft/`).

---

### 7. Transition status (explicit + safe)

Transition behavior must be explicit:

- If status is `"To Do"`, ask the user: "Transition this ticket to In Progress now?"
  - Only transition if the user confirms.
- If status is already `"In Progress"`, do not transition.
- If status is `"In Review"` or `"Done"`, warn and ask whether to proceed anyway (no automatic
  transition).

If transitioning, invoke the **managing-jira** skill:
- Apply **"Get Available Transitions"**
- Apply **"Transition Ticket"**

---

### 8. Display summary

Display a short summary:
- Ticket key + summary
- Status (and whether it was transitioned)
- Branch name
- Jira link
