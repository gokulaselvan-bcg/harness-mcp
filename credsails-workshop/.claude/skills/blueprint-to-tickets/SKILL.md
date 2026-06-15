---
name: blueprint-to-tickets
description: Decompose a blueprint into epics and implementation tickets in Jira-compatible markdown structure.
---

# /blueprint-to-tickets - Blueprint Decomposition Workflow

Decompose a project-level technical blueprint into actionable Jira-compatible tickets organized by epics.

## Usage

```bash
/blueprint-to-tickets
```

## Purpose

This workflow takes a project-level technical blueprint and decomposes it into actionable Jira-like tickets organized by epics that can be implemented incrementally. This is part of the **Lead Workflow**.

## Skill Reference

**Related skills for understanding ticket structure:**
- **managing-jira** - Jira ticket structure and field formats

---

## Step 1: List Available Blueprints

First, identify all available blueprint files under `artifacts/blueprints/`:

**Action:**
- List all `artifacts/blueprints/*/blueprint.md` files
- Present the list to the user with clear identifiers
- Ask if other documents should be included

**If no blueprints found:**
- Inform the user that no blueprints were found
- Suggest creating a blueprint first using the `/blueprint` command
- Ask if they want to decompose a different document

## Step 2: Prompt User to Select Blueprint

**Ask the user:**
- "Which blueprint would you like to decompose into tickets?"
- Show the list of available blueprint files with numbers or clear names
- Wait for user selection before proceeding

**User selection format:**
- Accept blueprint path (e.g., `artifacts/blueprints/proj-123--progress-tracking/blueprint.md`)
- Accept number if numbered list was provided
- Accept full path if needed

## Step 3: Read and Parse Selected Blueprint

**Actions:**
1. Read the full blueprint file
2. Extract metadata from frontmatter (if present):
   - Look for `id` field in YAML frontmatter
   - This is the canonical source for ticket ID and should be preferred
   - If no ID in frontmatter, only use directory fallback when the blueprint folder
     uses an unambiguous delimiter:
     `artifacts/blueprints/{id}--{name}/blueprint.md` -> `{id}`
   - Do not infer `{id}` by splitting on single hyphens in folder names because IDs can contain hyphens
     (for example, `PROJ-123`)
   - If still no ID found, ask user to provide an ID and recommend adding
     `id` to frontmatter for future runs

**ID extraction priority:**
1. Frontmatter metadata: `id`
2. Directory pattern with explicit delimiter: Extract `{id}` from
   `artifacts/blueprints/{id}--{name}/blueprint.md`
3. Ask user: "Please provide an ID for this blueprint's tickets" and suggest adding
   `id` to frontmatter

**Parse blueprint structure:**
- Identify all major sections (Context, Architecture Overview, Major Components, etc.)
- Identify all major components and their responsibilities
- Identify technical decisions and requirements
- Identify integration points and dependencies
- Identify implementation phases
- Note any open questions or risks

## Step 4: Analyze Blueprint and Identify Proposed Epics

Before creating tickets, analyze the blueprint and propose a set of epics that will organize the work.

### Epic Identification Strategy:

**Analyze the blueprint for:**
1. **Implementation Phases** (often map directly to epics)
2. **Major Components** (each may become one or more epics)
3. **Technical Layers** (e.g., Infrastructure, Database, API Layer, Frontend)
4. **Integration Points** (e.g., External Service Integration, Authentication Setup)
5. **Cross-Cutting Concerns** (e.g., Testing Infrastructure, Documentation, Deployment)

**Epic Structure Template:**

```markdown
### Epic [NUMBER]: [Epic Name]

**Type:** Epic

**Description:**
[2-3 sentences describing what this epic encompasses and why it's grouped together]

**Scope:**
- [ ] Major feature/component 1
- [ ] Major feature/component 2
- [ ] Major feature/component 3

**Key Deliverables:**
- Deliverable 1
- Deliverable 2
- Deliverable 3

**Effort Estimate:** [High | Medium | Low] (t-shirt size)

**Dependencies:**
- Depends on: [Other epic names or external systems]
- Blocks: [Other epic names that can't start until this is done]

**Related Blueprint Sections:**
- [Section references from original blueprint]

**Acceptance Criteria:**
- [ ] Epic-level acceptance criteria 1
- [ ] Epic-level acceptance criteria 2
- [ ] Epic-level acceptance criteria 3

**Notes:**
[Any important context or considerations for this epic]
```

### Create Proposed Epics:

Present a comprehensive list of proposed epics to the user. Each epic should:
- Represent a logical grouping of related functionality
- Be appropriately scoped (typically 3-8 tickets per epic)
- Have clear boundaries and deliverables
- Include dependencies on other epics
- Have an effort estimate (High/Medium/Low t-shirt size)

**Example Epic Categories:**
- Infrastructure & Setup
- Database Schema & Models
- Authentication & Authorization
- Core CRUD APIs
- Business Logic & Services
- Frontend Dashboard & Navigation
- Frontend Feature Components
- Integration with External Services
- Testing & Quality Assurance
- Documentation & Deployment

## Step 5: High-Level Epic Review (Phase 1)

**Present the proposed epics at a high level:**

1. Show the full list of epic names with brief descriptions
2. Show epic count and overall scope
3. Ask for high-level feedback:
   - "Do these epics align with your vision for this blueprint?"
   - "Are there any missing epics?"
   - "Should any epics be split, combined, or renamed?"
   - "Does the overall breakdown make sense?"

**Allow user to:**
- Approve the high-level structure
- Request modifications (split, combine, rename)
- Add new epics
- Remove epics
- Reorder epics

**Iterate until user approves the high-level epic structure.**

## Step 6: Detailed Epic Review and Epic Ticket Creation (Phase 2)

**For each epic, systematically review and create the epic ticket:**

Work through epics one at a time in the approved order.

### For Each Epic:

1. **Present Epic Details:**
   - Show full epic information (description, scope, deliverables, dependencies)
   - Show related blueprint sections
   - Present initial effort estimate and acceptance criteria

2. **Review with User:**
   - "Does this epic's scope look correct?"
   - "Are the deliverables complete?"
   - "Should we adjust the effort estimate (High/Medium/Low)?"
   - "Do the dependencies make sense?"
   - "Are the acceptance criteria appropriate for this epic?"
   - "Should we add, remove, or modify any acceptance criteria?"

3. **Iterate and Refine:**
   - Make adjustments based on user feedback
   - Confirm final epic details

4. **Create Main Tickets File (if first epic) and Add Epic Ticket:**
   - Create tickets folder (if needed): `artifacts/blueprints/{id}--{name}/tickets/`
   - Create main tickets file if this is the first epic: `artifacts/blueprints/{id}--{name}/tickets/{id}-tickets.md`
   - Create subdirectory: `artifacts/blueprints/{id}--{name}/tickets/{id}-tickets/` (will be used for epic ticket files)
   - Add epic ticket to the main tickets file in the "Epic Tickets" section
   - Use the epic structure template with all agreed-upon details
   - Format: `EPIC-[NUMBER]-[short-name]` (e.g., `EPIC-01-Infrastructure-Setup`)
   - Each epic ticket should start with a checkbox: `- [ ] **EPIC-[NUMBER]-[SHORT-NAME]: [Name]**`

**Epic Ticket Format:**

```markdown
- [ ] **EPIC-[NUMBER]-[SHORT-NAME]: [Epic Name]**

**Issue Type:** Epic

**Summary:** [Epic Name]

**Effort Estimate:** [High | Medium | Low] (for reference only)

**Labels:** [comma-separated labels, e.g., backend, infrastructure, database]

**Description:**
[2-3 sentences describing what this epic encompasses and why it's grouped together]

**Scope:**
- [ ] Major feature/component 1
- [ ] Major feature/component 2
- [ ] Major feature/component 3

**Key Deliverables:**
- Deliverable 1
- Deliverable 2
- Deliverable 3

**Dependencies:**
- Depends on: [Other epic names or external systems]
- Blocks: [Other epic names that can't start until this is done]

**Acceptance Criteria:**
- [ ] Epic-level acceptance criteria 1 (testable and specific)
- [ ] Epic-level acceptance criteria 2
- [ ] Epic-level acceptance criteria 3

**Related Blueprint Sections:**
- [Section references from original blueprint]

**Notes:**
[Any important context or considerations for this epic]

---
```

5. **Move to Next Epic:**
   - Repeat the process for the next epic
   - Continue until all epics have been reviewed and epic tickets created

**Once all epics have been reviewed and epic tickets created, proceed to create implementation tickets.**

## Step 7: Create Tickets Epic by Epic (in Separate Files by Epic)

For each approved epic, create the associated tickets and save them to separate files organized by epic within a subdirectory. Work through epics one at a time, creating all tickets for an epic, then reviewing with the user before moving to the next epic.

**File Organization:**
- Main tickets file: `artifacts/blueprints/{id}--{name}/tickets/{id}-tickets.md` - Contains epic definitions and references to ticket files
- Subdirectory: `artifacts/blueprints/{id}--{name}/tickets/{id}-tickets/` - Contains individual epic ticket files
- Epic ticket files: `artifacts/blueprints/{id}--{name}/tickets/{id}-tickets/EPIC-[NUMBER]-[SHORT-NAME].md` - Contains all tickets for that epic

### Ticket Structure Template (Jira-Compatible):

```markdown
- [ ] **[EPIC-PREFIX]-[NUMBER]: [Short Descriptive Title]**

**Issue Type:** [Epic | Task | Subtask]

**Summary:** [Short Descriptive Title] (required - max 255 characters)

**Effort Estimate:** [High | Medium | Low] (t-shirt size - for reference only, not a Jira field)

**Labels:** [comma-separated labels, e.g., backend, api, database, frontend, testing]

**Parent Epic:** EPIC-[NUMBER]-[SHORT-NAME] ([Epic Name]) - For Task/Subtask issues, use this to link to parent epic

**Description:**
[Clear, detailed description of what needs to be implemented, 2-4 sentences. Include context and business value.]

**Acceptance Criteria:**
- [ ] Criterion 1 (testable, specific, and measurable)
- [ ] Criterion 2
- [ ] Criterion 3
- [ ] Criterion 4 (if applicable)

**Technical Details:**

**Database Changes (if any):**
- Table: [table name]
- Columns: [new/modified columns]
- Migrations: [migration file name or description]
- Indexes: [new indexes needed]

**API Endpoints (if any):**
- Method: [GET | POST | PUT | PATCH | DELETE]
- Path: `/api/v1/...`
- Request Schema: [describe request body/params]
- Response Schema: [describe response structure]
- Status Codes: [list expected status codes]

**Frontend Components (if any):**
- Component Name: [name]
- Props: [props interface]
- State: [state management approach]
- Styling: [styling approach]

**Dependencies:**
- Blocks: [ticket numbers/names that must be completed first]
- Is Blocked By: [ticket numbers/names that block this ticket]
- Related To: [other tickets that are related but not blocking]

**Testing Requirements:**
- Unit Tests: [describe what needs unit testing]
- Integration Tests: [describe what needs integration testing]
- E2E Tests: [describe what needs end-to-end testing]
- Manual Testing: [describe any manual testing needed]

**Related Sections from Blueprint:**
- [Section name and reference, e.g., "Section 4.1: Component Architecture - User Service"]

**Implementation Notes:**
- [Any specific implementation guidance]
- [Patterns to follow from existing codebase]
- [Performance considerations]
- [Security considerations]

**Definition of Done:**
- [ ] Code implemented and reviewed
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] API documented (if applicable)
- [ ] Migration tested (if applicable)
- [ ] No linter errors
- [ ] Meets acceptance criteria
```

### Decomposition Strategy per Epic:

**1. Analyze Epic Scope**
- Identify all components mentioned in the epic
- List all acceptance criteria from blueprint sections
- Identify technical requirements

**2. Break Down into Tickets**
- Create tickets that are:
  - **Atomic**: One ticket = one complete, testable deliverable
  - **Independent**: Can be worked on separately (or with clear dependencies)
  - **Appropriately sized**: Should have clear effort estimate (High/Medium/Low)
  - **Testable**: Has clear acceptance criteria

**3. Ticket Granularity Guidelines**
- **Too granular**: "Create User model class" (too small, combine with migration)
- **Good granularity**: "Implement User CRUD API endpoints with validation and error handling"
- **Too broad**: "Build entire authentication system" (should be multiple tickets: registration, login, token management, middleware)

**4. Order Tickets Within Epic**
- Identify dependencies between tickets
- Order logically (e.g., database → API → frontend)
- Number tickets sequentially: `[EPIC-PREFIX]-001`, `[EPIC-PREFIX]-002`, etc.
- Create a slug from the ticket title for use in filename (lowercase, hyphens, no special chars)

**5. Determine Ticket Types**
- **Epic**: Major feature grouping (only for epic tickets)
- **Task**: Standard implementation work (use this for most tickets)
- **Subtask**: Use sparingly, only if a ticket needs to be broken down further into smaller pieces

**6. Note Effort Estimates (for reference only)**
- **High**: Complex work, significant effort required
- **Medium**: Moderate complexity and effort
- **Low**: Straightforward, minimal effort
- Note: These are for planning purposes only - Jira project may not have priority/effort fields

**7. Add Labels**
- Use consistent labels across tickets (e.g., `backend`, `frontend`, `api`, `database`, `testing`)
- Labels help categorize and filter tickets in Jira

### Process for Each Epic:

1. **Present Epic Context**
   - Show the epic details (EPIC-[NUMBER]-[SHORT-NAME])
   - Explain what tickets will be created for this epic
   - Show ticket count and effort estimate

2. **Create All Tickets for Epic**
   - Generate all tickets for the epic using the ticket template
   - Ensure dependencies are marked
   - Verify acceptance criteria are complete
   - Number tickets sequentially: `[EPIC-PREFIX]-001`, `[EPIC-PREFIX]-002`, etc.

3. **Create Epic Ticket File in Subdirectory**
   - Create subdirectory if it doesn't exist: `artifacts/blueprints/{id}--{name}/tickets/{id}-tickets/`
   - Create epic ticket file: `artifacts/blueprints/{id}--{name}/tickets/{id}-tickets/EPIC-[NUMBER]-[SHORT-NAME].md`
   - Add epic header section to the file:
     ```markdown
     ### EPIC-[NUMBER]-[SHORT-NAME]: [Epic Name]

     **Epic Details:**
     [Epic description, scope, deliverables - copy from epic ticket in main file]
     ```
   - Add all tickets for this epic to the file
   - Each ticket should start with a checkbox: `- [ ] **TICKET-ID: Title**`
   - Use the ticket template structure for each ticket
   - Tickets are organized within their epic file

4. **Update Main Tickets File with Reference**
   - After creating the epic ticket file, add a reference section to the main tickets file
   - The main file should have a section "Implementation Tickets by Epic" that references the separate files
   - Add entry: `- [EPIC-[NUMBER]-[SHORT-NAME]](./{id}-tickets/EPIC-[NUMBER]-[SHORT-NAME].md) - [Epic Name] ([X] tickets)`

5. **Present Tickets for Review**
   - List all tickets created for this epic
   - Show ticket titles, effort estimates, and key dependencies
   - Display the epic ticket file created

6. **Review and Validate Epic Tickets with User** (REQUIRED)
   - Present tickets in a checklist format for validation
   - Ask: "Please review the tickets for this epic. Do they look correct?"
   - Allow user to:
     - Approve tickets and move to next epic
     - Request modifications to specific tickets
     - Request additional tickets
     - Request to split or combine tickets
   - **Wait for user approval before proceeding to next epic**

7. **Make Adjustments if Needed**
   - If user requests changes, update the affected tickets in the epic ticket file
   - Re-save the epic ticket file
   - Re-present for review until approved

8. **Move to Next Epic**
   - Once current epic is approved, move to the next epic
   - Repeat the process for each epic
   - Maintain ticket numbering consistency across epics
   - Track dependencies across epics

## Step 8: Finalize Tickets File Structure

After all epics have been processed and all tickets added to their respective epic files, ensure the file structure is complete:

### Main Tickets File Structure (`artifacts/blueprints/{id}--{name}/tickets/{id}-tickets.md`):

```markdown
---
generated: YYYY-MM-DD
source_blueprint: artifacts/blueprints/{id}--{name}/blueprint.md
blueprint_id: [id-extracted-from-blueprint]
total_tickets: [number]
epics_count: [number]
---

# Implementation Tickets: [Blueprint Name]

**Source Blueprint:** `artifacts/blueprints/{id}--{name}/blueprint.md`

## Summary

This document contains [N] implementation tickets decomposed from [blueprint name], organized into [X] epics.

**Quick Stats:**
- Total Tickets: [N]
- Total Epics: [X]
- Epic Effort Breakdown: [X High, Y Medium, Z Low]

**Epics Overview:**
- EPIC-01-[SHORT-NAME]: [Name] ([X] tickets, [Effort: High/Medium/Low])
- EPIC-02-[SHORT-NAME]: [Name] ([X] tickets, [Effort: High/Medium/Low])
- ...

**Recommended Implementation Order:**
1. [Epic name] - [Reason why first]
2. [Epic name] - [Reason why second]
3. ...

**Dependency Graph:**
```
Epic 1 (Infrastructure)
  └─> Epic 2 (Database Schema)
       └─> Epic 3 (Core APIs)
            ├─> Epic 4 (Frontend Components)
            └─> Epic 5 (Testing)
```

---

## Epic Tickets

[Epic tickets created in Step 6 are listed here first, each with a checkbox]

- [ ] **EPIC-01-[SHORT-NAME]: [Epic Name]**

**Issue Type:** Epic

**Effort Estimate:** [High | Medium | Low] (for reference only)

**Labels:** [comma-separated labels]

**Description:**
[Epic description]

**Scope:**
- [ ] Major feature/component 1
- [ ] Major feature/component 2

**Key Deliverables:**
- Deliverable 1
- Deliverable 2

**Dependencies:**
- Depends on: [Other epic names]
- Blocks: [Other epic names]

**Acceptance Criteria:**
- [ ] Epic-level acceptance criteria 1
- [ ] Epic-level acceptance criteria 2

**Related Blueprint Sections:**
- [Section references]

**Notes:**
[Any important context or considerations for this epic]

---

[Repeat for each epic ticket]

---

## Implementation Tickets by Epic

Detailed implementation tickets for each epic have been separated into individual files within the `{id}-tickets/` subdirectory. Each epic's tickets are organized in their own file for easier navigation and management.

**Epic Ticket Files:**
- [EPIC-01-[SHORT-NAME]](./{id}-tickets/EPIC-01-[SHORT-NAME].md) - [Epic Name] ([X] tickets)
- [EPIC-02-[SHORT-NAME]](./{id}-tickets/EPIC-02-[SHORT-NAME].md) - [Epic Name] ([X] tickets)
- ...

**Note:** Epic definitions and summaries remain in this document above. For detailed task breakdowns, acceptance criteria, and implementation notes, please refer to the individual epic files linked above.
```

### Epic Ticket File Structure (`artifacts/blueprints/{id}--{name}/tickets/{id}-tickets/EPIC-[NUMBER]-[SHORT-NAME].md`):

```markdown
### EPIC-[NUMBER]-[SHORT-NAME]: [Epic Name]

**Epic Details:**
[Epic description, scope, deliverables - summary from main file]

- [ ] **[EPIC-PREFIX]-001: [Ticket Title]**

**Issue Type:** Task (or Subtask if breaking down further)

**Summary:** [Ticket Title] (required - max 255 characters)

**Effort Estimate:** [High | Medium | Low] (for reference only)

**Labels:** [comma-separated labels, e.g., backend, api, database, frontend, testing]

**Parent Epic:** EPIC-[NUMBER]-[SHORT-NAME] ([Epic Name])

**Description:**
[Ticket description]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

[Full ticket details...]

---

- [ ] **[EPIC-PREFIX]-002: [Ticket Title]**

[Full ticket details...]

---

[Repeat for each ticket in the epic]
```

## Step 9: Final Review of All Tickets

After all epics have been processed:

**Present comprehensive summary to user:**
- Total number of tickets generated
- Breakdown by epic (tickets per epic, effort estimate per epic)
- Breakdown by type (Epic, Task, Subtask)
- Breakdown by effort (High, Medium, Low) - for reference only
- Overall dependency structure

**Ask for final feedback:**
- "Are all tickets at the right level of granularity?"
- "Should any tickets be split or combined?"
- "Are there any missing tickets based on the blueprint?"
- "Are the dependencies correctly identified across epics?"
- "Does the implementation order make sense?"
- "Are the effort estimates (High/Medium/Low) reasonable?"

**Make adjustments based on feedback before saving.**

**Note:** All tickets are created in Step 7 and saved to separate epic files in the subdirectory. The main tickets file contains epic definitions and references to the epic ticket files.

## Step 10: Finalize and Save Tickets Files

**Actions:**
1. Ensure `artifacts/blueprints/{id}--{name}/tickets/` directory exists (create if needed)
2. Ensure subdirectory `artifacts/blueprints/{id}--{name}/tickets/{id}-tickets/` exists (create if needed)
3. Update main tickets file with references to all epic ticket files
4. Verify all epic ticket files are created in the subdirectory
5. Verify the main file structure is correct (epic tickets at top, then references to epic ticket files)
6. Open the main tickets file for user review

**Final confirmation:**
- Display: "Tickets saved to:"
  - Main file: `artifacts/blueprints/{id}--{name}/tickets/{id}-tickets.md` (contains epic definitions)
  - Epic ticket files: `artifacts/blueprints/{id}--{name}/tickets/{id}-tickets/EPIC-[NUMBER]-[SHORT-NAME].md` (contains detailed tickets)
- Show summary:
  - "[N] tickets generated across [X] epics"
  - "[X] epic tickets created in main file"
  - "[X] epic ticket files created in subdirectory"
  - "Epics: [list of epic names with effort estimates]"
- Mention: "Epic definitions are in the main file. Detailed tickets are organized by epic in separate files within the subdirectory. You can now use `/ticket-to-jira` to export these tickets to your Jira project. Update the checkboxes as work progresses."

**Note:** Tickets are created in separate epic files during Step 7. The main file structure is finalized in Step 8 and all files are saved/verified in Step 10.

## Best Practices

1. **Atomic Tickets**: Each ticket should represent a single, complete deliverable
2. **Clear Dependencies**: Explicitly state which tickets must be completed first
3. **Testable Criteria**: All acceptance criteria should be verifiable
4. **Realistic Estimation**: Consider complexity, not just lines of code
5. **Reference Source**: Always link back to the original blueprint section
6. **Consider Edge Cases**: Include tickets for error handling, validation, etc.
7. **Documentation**: Include tickets for updating documentation alongside features
8. **Testing**: Ensure test tickets are included for significant features
9. **Incremental Delivery**: Structure epics and tickets for incremental value delivery
10. **Alignment with Phases**: Consider blueprint implementation phases when organizing epics
