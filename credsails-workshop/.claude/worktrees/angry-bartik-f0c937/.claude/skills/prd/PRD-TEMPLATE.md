# Product Requirements Document Template

## Document Metadata

| Field | Description | Guidance |
|-------|-------------|----------|
| **Document Status** | [Draft/In Review/Final/Approved] | Start with "Draft", update as document progresses through review cycles |
| **Document Owner** | [Name] | Primary PM or product lead responsible for this feature |
| **Designer(s)** | [Names] | UX/UI designers involved |
| **Developer(s)** | [Names] | Engineering leads or key developers |
| **Stakeholder(s)** | [Names/Roles] | Key business stakeholders, external partners, or dependent teams |
| **Version History** | V1 - Initial Draft (Date)<br>V2 - [Description] (Date) | Track major revisions and what changed |
| **Related Documents** | [Links to related PRDs, technical specs, designs] | Include links to dependencies or related features |

## Executive Summary
*[1-2 paragraphs providing a high-level overview of what this feature/integration accomplishes and why it matters. This should be understandable by someone not familiar with the technical details.]*

**Key Questions for AI/Agent:**
- What is the core business problem being solved?
- Who are the primary users/customers affected?
- What is the expected business impact?

---

## Goals

### Primary Goals
*[List 3-5 primary objectives this feature must accomplish]*

1. **[Goal 1]**: [Detailed description of what success looks like]
2. **[Goal 2]**: [Detailed description of what success looks like]
3. **[Goal 3]**: [Detailed description of what success looks like]

### Success Metrics
*[Define measurable outcomes that indicate success]*

| Metric | Target | Measurement Method | Notes |
|--------|--------|-------------------|-------|
| [Metric 1] | [Target value] | [How measured] | [Context/rationale] |
| [Metric 2] | [Target value] | [How measured] | [Context/rationale] |

**Key Questions for AI/Agent:**
- What specific, measurable outcomes indicate success (and are they aligned with any SOW commitments)?
- How will we know if users are adopting this feature?
- What operational metrics should improve?

---

## Definitions & Terminology

| Term | Definition | Context/Example |
|------|------------|-----------------|
| [Term 1] | [Clear definition] | [When/how it's used] |
| [Term 2] | [Clear definition] | [When/how it's used] |

*[Add all domain-specific terms, acronyms, or concepts that readers need to understand]*

---

## Assumptions & Prerequisites

### Assumptions
| Assumption | Rationale | Risk if Invalid |
|------------|-----------|-----------------|
| [Assumption 1] | [Why we believe this] | [Impact if wrong] |
| [Assumption 2] | [Why we believe this] | [Impact if wrong] |

### Prerequisites
| Prerequisite | Description | Status |
|--------------|-------------|---------|
| [Prerequisite 1] | [What must be in place] | [Current state] |
| [Prerequisite 2] | [What must be in place] | [Current state] |

**Key Questions for AI/Agent:**
- What technical or functional capabilities must already exist?
- What organizational capabilities or processes are assumed?
- What third-party dependencies exist?

---

## Scope

### In Scope
*[Clearly define what this PRD covers]*

- [ ] [Feature/capability 1]
- [ ] [Feature/capability 2]
- [ ] [Integration point 1]

### Out of Scope / Not Doing
*[Explicitly list what is NOT included to prevent scope creep]*

| Functionality | Reason for Exclusion | Future Consideration? |
|---------------|---------------------|----------------------|
| [Feature] | [Why not included] | [Yes/No - Timeline if Yes] |

### Open Questions
| # | Question | Context/Impact | Owner | Target Resolution Date |
|---|----------|---------------|-------|----------------------|
| 1 | [Question] | [Why this matters] | [Who will resolve] | [Date] |

**Key Questions for AI/Agent:**
- What specific features or capabilities are explicitly excluded?
- Are there edge cases or scenarios not being addressed?
- What decisions are still pending?

---

## User Stories / Job Stories

### Goal 1: [Goal Name from Primary Goals]
*[Brief context about this goal and the users it affects]*

| As a... | I want... | So that I... | Acceptance Criteria |
|---------|-----------|--------------|-------------------|
| [Role] | [Action/capability] | [Outcome/value] | [How we verify success] |
| [Role] | [Action/capability] | [Outcome/value] | [How we verify success] |

### Goal 2: [Goal Name from Primary Goals]
*[Brief context about this goal and the users it affects]*

| As a... | I want... | So that I... | Acceptance Criteria |
|---------|-----------|--------------|-------------------|
| [Role] | [Action/capability] | [Outcome/value] | [How we verify success] |
| [Role] | [Action/capability] | [Outcome/value] | [How we verify success] |

### Goal 3: [Goal Name from Primary Goals]
*[Brief context about this goal and the users it affects]*

| As a... | I want... | So that I... | Acceptance Criteria |
|---------|-----------|--------------|-------------------|
| [Role] | [Action/capability] | [Outcome/value] | [How we verify success] |
| [Role] | [Action/capability] | [Outcome/value] | [How we verify success] |

*[Add sections for additional goals as needed]*

**Key Questions for AI/Agent:**
- Who are the different types of users affected by each goal?
- What are the primary workflows needed to achieve each goal?
- What problems are users trying to solve related to each goal?
- How does each user story contribute to achieving its associated goal?

---

## Functional Requirements

### Goal 1: [Goal Name from Primary Goals]

| ID | Requirement | Priority | Notes | Technical Considerations |
|----|-------------|----------|-------|-------------------------|
| R1.1 | [Specific requirement] | [Must/Should/Could] | [Context] | [Technical implications] |
| R1.2 | [Specific requirement] | [Must/Should/Could] | [Context] | [Technical implications] |

### Goal 2: [Goal Name from Primary Goals]

| ID | Requirement | Priority | Notes | Technical Considerations |
|----|-------------|----------|-------|-------------------------|
| R2.1 | [Specific requirement] | [Must/Should/Could] | [Context] | [Technical implications] |
| R2.2 | [Specific requirement] | [Must/Should/Could] | [Context] | [Technical implications] |

### Goal 3: [Goal Name from Primary Goals]

| ID | Requirement | Priority | Notes | Technical Considerations |
|----|-------------|----------|-------|-------------------------|
| R3.1 | [Specific requirement] | [Must/Should/Could] | [Context] | [Technical implications] |
| R3.2 | [Specific requirement] | [Must/Should/Could] | [Context] | [Technical implications] |

*[Add sections for additional goals as needed]*

### Integration Requirements
*[If applicable - for features that integrate with other systems]*

| Integration Point | Direction | Data Format | Authentication | Error Handling |
|-------------------|-----------|-------------|----------------|----------------|
| [System/API] | [Inbound/Outbound/Bidirectional] | [Format] | [Method] | [Strategy] |

### Data Requirements

| Data Element | Source | Format | Storage | Retention | Privacy Considerations |
|--------------|--------|--------|---------|-----------|----------------------|
| [Element] | [Where from] | [Format] | [Where stored] | [How long] | [PII/Sensitive?] |

**Key Questions for AI/Agent:**
- What are the must-have vs nice-to-have features for each goal?
- What data flows through the system to support each goal?
- What are the performance requirements for each goal?
- What are the security/privacy requirements for each goal?
- How should the system handle errors or edge cases for each goal?

---

## User Experience (UX) Requirements

### User Flows

#### Flow 1: [Flow Name/Scenario]
*[Describe this user journey through the feature]*

1. **Entry Point**: [How users access this feature]
2. **Key Steps**:
   - Step 1: [Description]
   - Step 2: [Description]
3. **Success State**: [What users see when successful]
4. **Error States**: [How errors are communicated]

#### Flow 2: [Flow Name/Scenario]
*[Describe this user journey through the feature]*

1. **Entry Point**: [How users access this feature]
2. **Key Steps**:
   - Step 1: [Description]
   - Step 2: [Description]
3. **Success State**: [What users see when successful]
4. **Error States**: [How errors are communicated]

*[Add additional flows as needed]*

### UI Components

| Component | Description | Behavior | Design Notes |
|-----------|-------------|----------|--------------|
| [Component 1] | [What it is] | [How it works] | [Visual/interaction notes] |

### Design Specifications
- **Figma/Design Links**: [Links to design files]
- **Accessibility Requirements**: [WCAG compliance level, specific needs]
- **Responsive Design**: [Mobile, tablet, desktop considerations]
- **Internationalization**: [Language/locale requirements]

**Key Questions for AI/Agent:**
- What is the primary user workflow? What are secondary workflows?
- What are the key screens/interfaces?
- What error messages or warnings are needed?
- How should the UI adapt to different devices/contexts?
---

## Testing & Validation

### UAT (User Acceptance Testing) Scenarios

| Scenario | User/Role | Steps to Test | Expected Result | Priority |
|----------|-----------|---------------|-----------------|----------|
| [Scenario 1] | [User type] | [Test steps] | [Expected outcome] | [P0/P1/P2] |
| [Scenario 2] | [User type] | [Test steps] | [Expected outcome] | [P0/P1/P2] |

### Acceptance Criteria Checklist
- [ ] [Specific, testable criteria 1]
- [ ] [Specific, testable criteria 2]
- [ ] [Specific, testable criteria 3]

---

## Dependencies & Risks

### Dependencies
| Dependency | Type | Owner | Status | Mitigation if Delayed |
|------------|------|-------|--------|---------------------|
| [Dependency] | [Internal/External/Technical] | [Team/vendor] | [Status] | [Plan B] |

### Risks
| Risk | Probability | Impact | Mitigation Strategy | Owner |
|------|-------------|--------|-------------------|-------|
| [Risk description] | [High/Medium/Low] | [High/Medium/Low] | [How to address] | [Who owns] |

---

## Change Log
| Date | Change | Author | Reason |
|------|--------|--------|--------|
| [Date] | [What changed] | [Who] | [Why] |

---

# Instructions for AI/Agent Use

When using this template to create a PRD, follow these steps:

## 1. Initial Information Gathering
Start by asking for:
- The feature/capability name and brief description
- Primary users and use cases
- Business objectives and success metrics
- Technical constraints or requirements
- Timeline and priority

## 2. Progressive Elaboration
For each section, if information is not provided:
- Ask specific, clarifying questions marked as "Key Questions for AI/Agent"
- Flag sections that need stakeholder input vs those you can reasonably infer

## 3. Completeness Checks
Before finalizing:
- Verify all user stories have acceptance criteria
- Confirm all requirements are testable
- Check that success metrics are measurable
- Validate that scope is clearly defined (both in and out)

## 4. Adaptive Sections
Based on the feature type, emphasize different sections:
- **For Integrations**: Focus on API specs, data flow, error handling
- **For User-Facing Features**: Emphasize UX requirements, user stories
- **For Compliance Features**: Expand security and compliance sections

## 5. Quality Guidelines
- Use clear, unambiguous language
- Avoid jargon without definitions
- Include specific examples where helpful
- Make requirements testable and measurable
- Ensure consistency across sections
