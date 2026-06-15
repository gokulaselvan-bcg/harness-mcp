---
name: managing-jira
description: Jira integration via Atlassian MCP for ticket operations, transitions, and ticket.md generation. Use when the user needs to pull tickets, check ticket status, transition tickets, or generate ticket.md files from Jira data.
---

# Managing Jira Skill

Provides Jira integration capabilities via the Atlassian MCP (Model Context Protocol).

## Prerequisites

**CRITICAL: This skill requires the Atlassian MCP server to be configured and authenticated.**

---

## Operations

### 1. Verify MCP Availability

**Before any Jira operation, verify MCP is available:**

```
1. Call `mcp_atlassian_atlassianUserInfo()` (no parameters required)
2. This returns user information if MCP is properly configured
```

**If MCP is NOT available or authentication fails:**
- Display error: "Atlassian MCP is not configured or not authenticated"
- **Stop the workflow immediately** - do not attempt alternative methods
- Provide guidance:
  ```
  The Atlassian MCP server is required but is not currently available.

  To configure Atlassian MCP:
  1. Ensure the Atlassian MCP server is configured in your Cursor settings
  2. Authenticate with your Atlassian account
  3. Verify access by checking MCP server status in Cursor settings

  Once configured and authenticated, restart this workflow.
  ```
- **Exit workflow** - do not proceed

**If MCP is available:**
- Display confirmation: "Atlassian MCP is configured and authenticated"
- Proceed with Jira operations

**Important:** Do not attempt to use command-line tools or other alternative methods for Jira access.

---

### 2. Get Cloud ID

**Get the Atlassian cloud ID for API calls:**

```
Call: mcp_atlassian_getAccessibleAtlassianResources()
Extract: cloudId from the response
```

Store the cloudId for subsequent Jira API calls.

---

### 3. Get Ticket Details

**Retrieve complete ticket details:**

```
Call: mcp_atlassian_getJiraIssue(cloudId, issueIdOrKey)
```

**Extract from response:**
- Ticket key (e.g., `PROJ-123`)
- Summary (title)
- Description (full markdown description)
- Status (To Do, In Progress, In Review, Done, etc.)
- Issue Type (Epic, Task, Subtask)
- Priority (High, Medium, Low)
- Issue Links (`issuelinks` field) - blockers/blocked relationships
- Labels
- Parent Epic (if task/subtask)
- Created/Updated dates

**From Description, extract:**
- Acceptance Criteria
- Technical Details
- Dependencies (Blocks:, Is Blocked By:)
- Related Spec Sections
- Implementation Notes
- Definition of Done

**Check Blockers:**
- Parse `issuelinks` array for blocking relationships
- For each blocker, check its status:
  - If blocker status is "Done" → ticket is unblocked
  - If blocker status is "To Do" or "In Progress" → ticket is blocked

---

### 4. Get Available Transitions

**Get transitions available for a ticket:**

```
Call: mcp_atlassian_getTransitionsForJiraIssue(cloudId, issueIdOrKey)
```

**Common transitions:**
- "In Progress" (ID typically: `21`)
- "In Review" (ID varies)
- "Done" (ID varies)

**Handle missing transitions:**
- If desired transition not available, list available transitions
- Ask user if they want to proceed without status change or select different transition

---

### 5. Transition Ticket

**Move ticket to new status:**

```
Call: mcp_atlassian_transitionJiraIssue(cloudId, issueIdOrKey, transition={id: transitionId})
```

**Example - Move to In Progress:**
```
mcp_atlassian_transitionJiraIssue(cloudId, "PROJ-123", transition={id: "21"})
```

**Verify transition:**
- Get ticket again to confirm status changed
- Display confirmation: "Ticket moved to [NEW STATUS]"

---

### 6. Search Tickets with JQL

**Search for tickets using JQL:**

```
Call: mcp_atlassian_searchJiraIssuesUsingJql(cloudId, jql, fields, maxResults)
```

**Example JQL queries:**
- All TODO tickets: `project = PROJ AND status = "To Do" ORDER BY priority DESC, created ASC`
- My in-progress tickets: `project = PROJ AND status = "In Progress" AND assignee = currentUser()`

**Request fields:**
- `summary`, `status`, `priority`, `issuelinks`, `parent`, `created`, `updated`

---

## ticket.md Format

When generating `ticket.md`, use this format:

```markdown
# Current Ticket: [TICKET-KEY] - [Summary]

**Status:** [Status] (will be updated to "In Progress" after transition)
**Priority:** [High | Medium | Low]
**Type:** [Issue Type]
**Parent Epic:** [Epic Name] (if applicable)
**Labels:** [comma-separated labels]

**Blockers:**
- BLOCKED by: [TICKET-KEY] - [Summary] (Status: [Status]) - [Link]
  (or) No blockers - ticket is ready to work on

---

## Description

[Full ticket description with all sections]

## Acceptance Criteria

[Acceptance criteria list, formatted as checklist]

## Technical Details

[Technical details section if present]

## Dependencies

**Jira Issue Links:**
- **Blocks:** [list of tickets this blocks from issuelinks]
- **Blocked By:** [list of tickets that block this from issuelinks]
- **Related To:** [other related tickets from issuelinks]

## Testing Requirements

[Testing requirements if present]

## Implementation Notes

[Implementation notes if present]

## Definition of Done

[Definition of Done checklist if present]

---

**Jira Link:** https://bcgx.atlassian.net/browse/[TICKET-KEY]
**Branch:** `[prefix]/[branch-name]` (e.g., `ft/proj-123-short-description`)
```

**File Location:**
- Write to: `artifacts/tickets/[TICKET-KEY]/ticket.md`
- Create the directory if needed
- Overwrite `ticket.md` for the same ticket if it already exists

---

## Priority Indicators

| Priority | Indicator |
|----------|-----------|
| High     | High priority |
| Medium   | Medium priority |
| Low      | Low priority |

---

## Error Handling

**If ticket not found:**
- Inform user: "Ticket [TICKET-KEY] not found"
- Suggest checking ticket ID or Jira board

**If MCP unavailable:**
- Do NOT attempt alternative methods
- Display MCP configuration guidance
- Exit workflow gracefully

**If transition fails:**
- Show available transitions
- Ask user preference: proceed without change or try different transition
