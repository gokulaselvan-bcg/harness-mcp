---
name: prd
description: Create a product requirements document (PRD) from user context and references using the PRD template.
---

# Product Requirements Document (PRD) Creation Workflow

This workflow helps you create comprehensive Product Requirements Documents (PRDs) for features. PRDs should be created by **Product Managers** or **Product Leads** before creating technical blueprints. This is the first step in the requirements gathering process.

## References

Use the PRD template as the structural source of truth:
- [PRD-TEMPLATE.md](PRD-TEMPLATE.md)

## PRD vs Blueprint vs Design

- **PRD**: Product-level requirements covering business goals, user stories, and functional requirements for a feature
- **Blueprint (HLD)**: Project-level technical architecture covering multiple epics (references PRD)
- **Design (LLD)**: Ticket-level implementation details for a single task

## Step 1: Consolidated Information Gathering

**Gather all essential information in 1-2 focused rounds, not 11 separate section-by-section rounds.**

### Round 1: Core Context (Ask All Together)

Present all these questions in a single interaction:

**Feature & Problem:**
1. What feature/capability are you documenting? (Provide a feature name)
2. What is the business problem this solves?
3. What is the current state without this feature? (pain points, manual processes, bottlenecks)

**Users & Impact:**
4. Who are the primary users? (engineers, marketers, analysts, customers, etc.)
5. What is the expected business impact? (revenue, efficiency, user satisfaction, strategic value)

**Stakeholders & Team:**
6. Who is the document owner (PM/product lead)?
7. Who are the key designers, developers, and stakeholders involved?

**Goals & Success:**
8. What are the 3-5 primary objectives this feature must accomplish?
9. What specific, measurable outcomes indicate success? (targets, timelines)

**Documentation & Context:**
10. Do you have existing documentation? (API docs, mockups, designs, specs, related PRDs)
11. What is the scope? (What's explicitly included and excluded?)
12. What is the timeline or launch date?

### Round 2: Workflows & Technical Details (Ask All Together)

After receiving Round 1 answers, ask:

**User Workflows:**
1. For each user type mentioned, what are their key workflows/tasks?
2. What problems are they solving? What value do they get?

**Technical Requirements (if applicable):**
3. What type of integration is this? (API, SDK, webhook, bidirectional, etc.)
4. What data flows through the system? (events, users, transactions, etc.)
5. What are the volume/performance requirements? (requests/day, latency, etc.)
6. What are the security/auth requirements?

**Scope Clarification:**
7. Are there any specific features or partners you're integrating with?
8. Are there any open questions or decisions pending?

### Round 3: Clarifications Only (If Needed)

Only ask follow-up questions if:
- Critical information is genuinely ambiguous
- User provided conflicting information
- Documentation links are broken/inaccessible

**Don't ask if you can reasonably infer the answer from context or documentation.**

## Step 2: Intelligent Inference & Drafting

**After gathering information, use intelligent reasoning to draft content instead of asking more questions.**

### Infer from Documentation Links

When user provides API docs, integration guides, or technical specs:

**Extract automatically:**
- Authentication methods (API keys, OAuth, signatures)
- Request/response formats (JSON schemas, event structures)
- Rate limits and quotas
- Error codes and handling patterns
- Testing scenarios from API examples
- Integration patterns (webhooks, polling, batch, real-time)
- Data models (user attributes, events, entities)

**Example:** If user provides "https://docs.mparticle.com/developers/apis/http/"
- Infer: HTTP API integration, JSON event batches, Basic Auth, rate limiting, DLQ/retry needed
- Extract: Event schema, authentication pattern, error handling requirements
- Generate: Testing scenarios based on API examples

### Infer from Integration Type

**If "CDP integration" or "customer data platform":**
- Events: Outbound event streaming (user actions, purchases, etc.)
- Audiences: Inbound audience membership changes via webhook
- Identity: User ID, email, device ID for identity resolution
- Standard risks: Volume scaling, identity matching, partner API issues
- Testing: Event flow validation, audience sync, partner integration tests
- Definitions: CDP, event batch, audience, IDSync, webhook, real-time processing

**If "API integration" or "third-party service":**
- Authentication: API keys, OAuth tokens
- Error handling: Retry logic, DLQ for failed requests
- Monitoring: Request volume, latency, error rates
- Testing: Happy path, error cases, rate limiting
- Definitions: API endpoint, webhook, rate limit, authentication

**If "bidirectional integration":**
- Outbound: Data sent TO partner
- Inbound: Data received FROM partner
- Both directions need: Auth, error handling, monitoring
- Testing: Both directions validated separately

### Infer from User Types

**If users include "engineers":**
- User stories: Configure integration, manage API keys, monitor errors, debug issues
- UX needs: Admin panel for config, monitoring dashboard, logs/debugging tools
- Testing: Technical validation, API connectivity, error handling

**If users include "marketers":**
- User stories: Create audiences, launch campaigns, track performance, self-service without engineering
- UX needs: Self-service UI (likely in partner platform), monitoring dashboard (non-technical), email alerts
- Testing: End-to-end campaign launch, audience creation without engineering support

**If users include "data analysts" or "analytics teams":**
- User stories: Query data, build reports, validate data quality
- UX needs: Data access, dashboards, export capabilities
- Testing: Data accuracy, query performance, reporting

### Infer from Goals

**If goal mentions "engineering capacity" or "reduce engineering time":**
- Success metric: Time reduction (e.g., "from 2 weeks to 1 day")
- Risk: Timeline pressure to deliver quickly
- Out of scope: Custom integrations (use pre-built instead)
- User story: Engineers configure once, marketers self-serve after

**If goal mentions "self-service" or "without engineering support":**
- Functional requirement: UI for non-technical users
- UX requirement: Intuitive workflows, minimal training needed
- Testing: Non-technical user can complete tasks independently
- Risk: Adoption (will users actually use self-service?)

**If goal mentions "centralized" or "single source of truth":**
- Integration type: Data aggregation/consolidation
- Data requirements: Unified schema, identity resolution
- Testing: Data consistency across sources
- Definitions: Single source of truth, unified profile, data warehouse

### Propose Standard Sections (Don't Ask)

**Definitions & Terminology:**
- Use provided documentation to extract technical terms
- Include industry-standard terms based on feature type (CDP, API, webhook, etc.)
- Add 10-20 definitions by default; more comprehensive is better
- Don't ask permission—just include them

**User Stories:**
- Derive from stated goals and user types
- Format: "As a [user], I want [action], so that [value]"
- Add acceptance criteria: "Given/When/Then" or specific validation points
- Create 2-4 stories per goal, per user type

**Functional Requirements:**
- Extract from documentation (authentication, data formats, error handling)
- Infer must-haves from goals (e.g., "enable partner integrations" → "configure API connections")
- Add standard requirements: logging, monitoring, error handling, security
- Use priority: Must/Should/Could

**Testing Scenarios:**
- Generate from functional requirements and user workflows
- Include: Happy path, error cases, edge cases, performance tests
- Format: Scenario, user/role, steps, expected result, priority (P0/P1/P2)
- Create 15-20 scenarios for comprehensive coverage

**Risks & Mitigations:**
- Standard risks based on project type:
  - **Timeline risk**: Aggressive deadline, complex scope → Mitigation: Phased rollout, prioritize MVP
  - **Technical risk**: Volume/scaling, third-party dependencies → Mitigation: Load testing, fallback plans
  - **Integration risk**: Partner API changes, rate limits, downtime → Mitigation: Circuit breakers, monitoring
  - **Data quality risk**: Schema mismatches, identity resolution → Mitigation: Validation, comprehensive logging
  - **Adoption risk**: Users don't use new feature → Mitigation: Training, documentation, pilot program
  - **Security risk**: Unauthorized access, data leaks → Mitigation: Authentication, encryption, auditing
  - **Operational risk**: Service outages, dependencies fail → Mitigation: Retry logic, alerts, escalation plans

**UX Requirements:**
- Infer from user types and stated workflows
- Engineers: Admin panels, monitoring dashboards, logs
- Marketers: Self-service UI (often in partner platform), simple monitoring
- If "no UI needed", focus on APIs, monitoring, alerting

**Assumptions & Prerequisites:**
- Listen carefully to what user says is "already set up" or "already exists"
- Don't keep asking about things explicitly confirmed as complete
- Mark prerequisites as "✅ Complete", "🟡 In Progress", or "⬜ To Be Built"

### Drafting Process

1. **Read the PRD template** ([`PRD-TEMPLATE.md`](PRD-TEMPLATE.md)) to understand structure
2. **Fill all sections** using gathered information and inferred content
3. **Don't leave sections empty**—if information is missing, mark as [TBD] or make reasonable inference
4. **Include comprehensive details**:
   - 10-20 definitions minimum
   - 2-4 user stories per goal per user type
   - 15-20 testing scenarios
   - 5-7 standard risks with mitigations
   - Detailed functional requirements from documentation

## Step 4: Determine PRD Name and Location

**Extract feature name and create filename automatically:**

1. **Get feature name from Step 1** (Round 1, Question 1)

2. **Convert to kebab-case:**
   - Example: "User Authentication" → "user-authentication"
   - Example: "Payment Integration" → "payment-integration"
   - Example: "mParticle Integration" → "mparticle-integration"

3. **Construct filename:**
   - Format: `{feature-name}-prd.md`
   - Example: `user-authentication-prd.md`

4. **Determine location:**
   - Directory: `artifacts/requirements/`
   - Full path: `artifacts/requirements/{feature-name}-prd.md`

5. **Don't ask for confirmation**—just use this filename and inform user at the end.

## Step 5: Populate PRD Template

**Use the template structure from [`PRD-TEMPLATE.md`](PRD-TEMPLATE.md) and fill in all sections:**

1. **Fill Document Metadata:**
   - Status: "Draft"
   - Owner, designers, developers, stakeholders from Round 1
   - Version: "V1 - Initial Draft (current date)"
   - Related documents: Links provided in Round 1

2. **Fill Executive Summary:**
   - 1-2 paragraphs synthesizing: feature, problem, users, business impact
   - Use information from Round 1

3. **Fill Goals & Success Metrics:**
   - Primary goals from Round 1 (3-5 goals)
   - Success metrics table with targets, measurement method, notes

4. **Fill Definitions & Terminology:**
   - Extract terms from provided documentation
   - Include industry-standard terms based on feature type
   - 10-20 definitions minimum (comprehensive is better)

5. **Fill Assumptions & Prerequisites:**
   - Note what user said is "already set up" (mark ✅ Complete)
   - Note what needs to be built (mark ⬜ To Be Built)
   - Don't ask again about confirmed prerequisites

6. **Fill Scope:**
   - In scope: From Round 1/2
   - Out of scope: Infer what's NOT included (advanced features, future phases)
   - Open questions: Any genuinely unanswered questions

7. **Fill User Stories:**
   - Create 2-4 stories per goal per user type
   - Format: "As a [user], I want [action], so that [value]"
   - Add acceptance criteria for each

8. **Fill Functional Requirements:**
   - Extract from documentation (auth, API specs, data formats)
   - Infer from goals and workflows
   - Group by goal, add priority (Must/Should/Could)
   - Include integration and data requirements tables

9. **Fill UX Requirements:**
   - Infer from user types and workflows
   - User flows: Entry point, steps, success state, error states
   - UI components if applicable
   - For backend integrations, focus on monitoring/alerting UI

10. **Fill Testing & Validation:**
    - Generate 15-20 UAT scenarios from functional requirements
    - Include happy path, error cases, edge cases
    - Format: Scenario, user, steps, expected result, priority
    - Acceptance criteria checklist

11. **Fill Dependencies & Risks:**
    - Dependencies: From Round 2 or inferred
    - Standard risks: Timeline, technical, integration, data quality, adoption, security, operational
    - Include probability, impact, mitigation for each

12. **Add Change Log:**
    - Date: Current date
    - Change: "Initial Draft"
    - Author: Document owner name
    - Reason: "Initial PRD creation"

## Step 6: Save PRD File

**Save the completed PRD without asking for confirmation:**

1. **Create directory if needed:**
   ```bash
   mkdir -p artifacts/requirements
   ```

2. **Save the file:**
   - Full path: `artifacts/requirements/{feature-name}-prd.md`

3. **Verify file was created successfully**

## Step 7: Present Summary and Next Steps

**After saving, present a concise summary:**

1. **Display summary:**
   - PRD saved to: `artifacts/requirements/{feature-name}-prd.md`
   - Feature: `{feature-name}`
   - Goals: [N] primary objectives
   - User stories: [M] stories across [X] user types
   - Testing scenarios: [P] scenarios
   - Open questions: [Q] (if any)

2. **Next steps:**
   - "PRD is ready for review with stakeholders"
   - "Once approved, use `/blueprint` to create technical architecture"
   - "Blueprint will reference this PRD automatically"
   - (If open questions exist) "Resolve [Q] open questions before blueprint"

3. **Ask once:**
   - "Is there anything you'd like me to adjust in the PRD?"
   - Don't ask about additional documentation unless user requests it

## Best Practices

1. **Consolidated Information Gathering**: Ask all core questions in Round 1, technical details in Round 2 (2 rounds max, not 11)
2. **Use Documentation Proactively**: Read provided links to extract requirements, don't ask questions answered in docs
3. **Propose, Don't Ask**: Draft definitions, risks, testing scenarios—show user for approval instead of asking what to include
4. **Apply Context**: If user says something is "already set up", don't ask about it again
5. **Infer Intelligently**: Use 2nd/3rd order reasoning based on integration type, user types, and stated goals
6. **Be Comprehensive**: 10-20 definitions, 15-20 test scenarios, 5-7 risks—more detail is better
7. **Completeness**: Ensure all sections addressed, mark [TBD] only if genuinely unknown and couldn't be inferred
8. **Clarity**: Use clear, unambiguous language throughout
9. **Testability**: Make success metrics and acceptance criteria measurable
10. **Template Fidelity**: Follow the template structure exactly

## Guidelines

### Appropriate Level of Detail

**Include:**
- Business goals and expected outcomes
- User stories and workflows
- Functional requirements (what, not how)
- Success metrics and acceptance criteria
- Scope boundaries (in and out)
- Dependencies and risks

**Don't Include:**
- Technical implementation details (that's for `/blueprint`)
- Code-level specifications (that's for `/spec`)
- Task breakdowns (that's for `/plan`)

### When to Create a PRD

Create a PRD when:
- Starting a new feature or significant capability
- Need to align stakeholders on requirements
- Planning work that spans multiple epics
- Business requirements need to be documented
- Feature has complex user workflows or acceptance criteria

Don't create a PRD for:
- Small bug fixes or minor enhancements
- Internal technical improvements with no user impact
- Work already covered by existing PRD
- Exploratory or research tasks

### PRD Lifecycle

1. **Draft**: Initial PRD created, gathering requirements
2. **In Review**: PRD under review by stakeholders
3. **Final**: PRD reviewed and ready for technical planning
4. **Approved**: PRD approved and ready for blueprint creation

Update PRD status in metadata as it progresses.

## Example Workflow

**User**: "I need to create a PRD for user authentication"

**Assistant**: "I'll help you create a comprehensive PRD. Let me gather the essential information in two focused rounds."

**Round 1 - All Core Questions at Once:**

**Assistant**: "Please answer these questions about the user authentication feature:

**Feature & Problem:**
1. What feature are you documenting? (Provide a feature name)
2. What business problem does this solve?
3. What is the current state without this feature?

**Users & Impact:**
4. Who are the primary users?
5. What is the expected business impact?

**Stakeholders & Team:**
6. Who is the document owner, designers, developers, stakeholders?

**Goals & Success:**
7. What are the 3-5 primary objectives?
8. What specific, measurable outcomes indicate success?

**Documentation & Context:**
9. Do you have existing documentation?
10. What's in scope? What's out of scope?
11. What is the timeline?"

**User provides all answers at once**

**Round 2 - Technical Details:**

**Assistant**: "Thanks! Now for the technical details:

1. For each user type (engineers, end-users), what are their key workflows?
2. What type of authentication? (OAuth, SAML, API keys, etc.)
3. What data flows through the system?
4. Volume/performance requirements?
5. Security requirements?
6. Any open questions?"

**User provides technical answers**

**Assistant Actions:**
1. Read provided documentation links to extract auth patterns, API specs
2. Infer standard definitions (OAuth, SAML, JWT, session, etc.)
3. Infer user stories from stated goals and user types
4. Extract functional requirements from documentation
5. Generate 15-20 testing scenarios (login, logout, password reset, MFA, etc.)
6. Propose standard risks (security breaches, adoption, integration with existing systems)
7. Draft complete PRD with all inferred content
8. Save to: `artifacts/requirements/user-authentication-prd.md`

**Assistant**: "PRD saved to `artifacts/requirements/user-authentication-prd.md`

Summary:
- Feature: User Authentication
- Goals: 3 primary objectives
- User stories: 8 stories (engineers, end-users)
- Testing scenarios: 18 scenarios
- Open questions: 2

Next steps: Use `/blueprint` to create technical architecture.

Is there anything you'd like me to adjust in the PRD?"

**Result**: Complete PRD with 2 rounds of questions (not 11)

## Error Handling

**If feature name is unclear:**
- Infer from context or ask: "What's a short, descriptive name for this feature?"

**If critical information is missing after Round 2:**
- First, try to infer from context, documentation, or industry standards
- Only if genuinely unknowable, mark as [TBD] in PRD
- Note in summary: "X items marked [TBD]—please clarify before blueprint"

**If user says something is "already set up" or "already exists":**
- Mark as ✅ Complete in Prerequisites
- Don't ask about it again in subsequent questions
- Pay attention to context clues

**If documentation links are broken/inaccessible:**
- Inform user: "Could not access [URL]—please verify link or provide alternative"
- Ask for alternative documentation or proceed with available information

**If directory creation fails:**
- Inform user: "Failed to create artifacts/requirements/ directory"
- Check permissions and retry
- Ask user to create directory manually if needed

**If file save fails:**
- Inform user: "Failed to save PRD file"
- Verify directory exists and is writable
- Retry or ask user to check permissions

## Relationship to Other Commands

**PRD → Blueprint:**
- PRD is created first
- Blueprint references PRD for business context
- Blueprint focuses on technical architecture
- Use `/blueprint` after PRD is approved

**PRD → Design → Plan:**
- PRD defines requirements
- Blueprint defines architecture
- Design defines ticket-level implementation
- Plan breaks down into tasks
- Workflow: `/prd` → `/blueprint` → `/spec` → `/plan` → `/implement`
