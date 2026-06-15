---
name: blueprint
description: Create project-level technical blueprints (HLD) from PRD/context with explicit architectural decisions and phased implementation guidance.
---

# Blueprint Agent Workflow

This workflow helps you create project-level technical blueprints that define architecture, major components, and high-level design decisions. Blueprints are created by **Tech Leads** and **Architects** as part of the **Lead Workflow**.

## Skills to Invoke

**IMPORTANT: You MUST first read and invoke these skills before proceeding:**

1. `spec` - For understanding ticket spec structure

## Blueprint vs Design

- **Blueprint (High-Level Design/HLD)**: Project-level architecture covering multiple epics and features
- **Design (Low-Level Design/LLD)**: Ticket-level implementation details for a single task

## Step 1: Gather High-Level Requirements and Documents

**First, ask for documents and references:**

**Questions to ask:**
- What initiative, feature set, or project needs a technical blueprint?
- **Do you have a PRD for this initiative?** (Ask for feature name or path to PRD file)
  - If PRD exists, read it from `artifacts/requirements/{feature-name}-prd.md`
  - Extract business goals, scope, user stories, and functional requirements from PRD
  - Use PRD as primary source for business context
- **Do you have a PRD, HLD, or requirements document?** (Ask user to provide the document or path)
- **Do you have mockups, wireframes, or design files?** (Ask user to provide files or links)
- **Are there any existing technical documents or architecture references?** (Ask for links or paths)
- What is the expected scope (number of features, epics, or components)?

**Gather documents first:**
1. **Request all documents upfront**: Ask the tech lead to provide all relevant documents before proceeding
2. **Read provided documents**: If paths are provided, read the documents to understand context
3. **Confirm document list**: Show what documents you have and ask if there are any others

**Documents to collect:**
- **PRD (Product Requirements Document)** - Primary source for business context
  - Location: `artifacts/requirements/{feature-name}-prd.md`
  - Extract: Business goals, scope, user stories, functional requirements, success metrics
- HLD (High-Level Design)
- Requirements documents
- Mockups, wireframes, or design files
- Timeline or delivery phases (if known)
- Related architecture documents
- External references or links

**After gathering documents, extract:**
- Initiative/project name
- PRD reference (if available)
- High-level description (from PRD or user input)
- Business objectives (from PRD)
- Key requirements (from PRD functional requirements)
- Timeline or delivery phases
- Stakeholder concerns

## Step 2: Review Existing Architecture and Research Technologies

Search the codebase and documentation for relevant architectural context:

**Search for:**
- Existing architecture documentation (ADRs, architecture.md)
- Similar features or systems already implemented
- Integration points with existing components
- Current technology stack and patterns
- Data models and schemas that may be affected
- External service integrations

**Review:**
- Current system architecture
- Technology choices and constraints
- Existing patterns and conventions
- Performance and scalability considerations
- Security and compliance requirements

**Research technologies and approaches (use web search):**

When technical decisions need to be made, use web search to understand:
- **Pros and cons of different approaches**: Search for "X vs Y comparison" or "pros and cons of X"
- **Best practices**: Search for "X best practices" or "X architecture patterns"
- **Performance characteristics**: Search for "X performance benchmarks" or "X scalability"
- **Community consensus**: Search for recent discussions and recommendations
- **Known issues**: Search for "X common problems" or "X gotchas"

**Examples of research topics:**
- Database choices: "PostgreSQL vs MongoDB for [use case]"
- API patterns: "REST vs GraphQL pros and cons"
- Authentication: "JWT vs session-based authentication comparison"
- Caching strategies: "Redis vs Memcached comparison"
- Message queues: "RabbitMQ vs Kafka use cases"
- Frontend frameworks: "React vs Vue performance comparison"

**Present research findings to user:**
- Show pros and cons for each option
- Highlight trade-offs and considerations
- Include performance and scalability factors
- Note community recommendations
- Reference authoritative sources

## Step 3: Ask for Additional Context

Present findings and ask if additional context is needed:

**Ask:**
- "I found [list of relevant architecture/context]. Is there anything else I should consider?"
- "Do you have design documents, architecture diagrams, or external references?"
- "Are there specific technical constraints or requirements? (performance, security, compliance)"
- "What are the key integration points with existing systems?"
- "What is the expected scale and load?"
- "Are there any architectural decisions already made that I should incorporate?"

**If additional context is needed:**
- Request specific architecture documents
- Ask about external dependencies or services
- Clarify non-functional requirements
- Identify key stakeholders and their concerns

## Step 4: Identify and Present Decision Points

Before creating the blueprint, identify key architectural decisions that need to be made and present them to the user with research-backed analysis.

**Identify decision points from:**
- Requirements analysis
- Technology choices
- Architecture patterns
- Integration approaches
- Data storage strategies
- Scalability approaches
- Security mechanisms

**For each decision point:**

1. **Present the decision clearly**:
   - "Decision needed: [Clear description of what needs to be decided]"
   - "Context: [Why this decision matters for this initiative]"

2. **Present options with research-backed analysis** (use web search for each option):

   **Option A: [Technology/Approach Name]**
   - **Pros**: [List with web research findings]
   - **Cons**: [List with web research findings]
   - **Best for**: [Use cases where this excels]
   - **Performance**: [Performance characteristics from research]
   - **Community**: [Adoption and support level]
   - **References**: [Links to authoritative sources]

   **Option B: [Technology/Approach Name]**
   - **Pros**: [List with web research findings]
   - **Cons**: [List with web research findings]
   - **Best for**: [Use cases where this excels]
   - **Performance**: [Performance characteristics from research]
   - **Community**: [Adoption and support level]
   - **References**: [Links to authoritative sources]

3. **Provide recommendation** (if applicable):
   - "Recommended: Option [X] because [reasoning based on requirements and constraints]"
   - Explain trade-offs and why this fits the specific use case
   - Note: Always defer to user's expertise and preferences

4. **Ask user to decide**:
   - "Which option would you like to proceed with?"
   - "Do you need more information about any option?"
   - "Are there other options we should consider?"
   - **Wait for user's decision before proceeding to blueprint generation**

**Example decision points:**

- **Database Selection**: PostgreSQL vs MongoDB vs DynamoDB
  - Consider: Data structure, query patterns, scalability needs, ACID requirements

- **API Design**: REST vs GraphQL vs gRPC
  - Consider: Client needs, performance, complexity, tooling

- **Authentication**: JWT vs OAuth2 vs SAML
  - Consider: Security requirements, user base, SSO needs

- **Caching Layer**: Redis vs Memcached vs CDN caching
  - Consider: Data types, persistence needs, distributed caching

- **Message Queue**: RabbitMQ vs Kafka vs AWS SQS
  - Consider: Message volume, ordering, durability, processing patterns

- **Frontend Framework**: React vs Vue vs Angular
  - Consider: Team expertise, ecosystem, performance, type safety

- **State Management**: Redux vs Context API vs Zustand vs MobX
  - Consider: App complexity, team size, debugging needs

- **Deployment Strategy**: Kubernetes vs Serverless vs VM-based
  - Consider: Scaling needs, cost, operational complexity, team skills

**Decision documentation:**
- Document each decision made and rationale
- Note which decisions should become ADRs
- Track dependencies between decisions (e.g., choosing Kafka may influence deployment strategy)
- Ensure decisions are consistent with requirements and constraints
- Record any dissenting opinions or alternatives discussed

**Decision presentation format:**

```
## Decision Point 1: [Decision Name]

**Context**: [Why this matters]

**Options Analyzed**:
1. [Option A]
   - Pros: [From research]
   - Cons: [From research]
   - References: [Links]

2. [Option B]
   - Pros: [From research]
   - Cons: [From research]
   - References: [Links]

**Recommendation**: [Option with reasoning]

**User Decision**: [Wait for user input]
```

## Step 5: Generate Blueprint Structure

Create a comprehensive project-level blueprint document with the following sections:

### Blueprint Template:

> **Canonical template**: [`BLUEPRINT-TEMPLATE.md`](BLUEPRINT-TEMPLATE.md) (co-located with this skill). The inline scaffold below mirrors that file as a quick reference; treat the canonical file as the source of truth and update both in lockstep until the inline scaffold is removed.

```markdown
---
created: YYYY-MM-DD
author: [Name]
id: [Unique ID - use project code, initiative name, or UUID]
related_prd: [Path to PRD file, e.g., artifacts/requirements/{feature-name}-prd.md]
related_hld: [HLD reference]
status: draft
---

# [Initiative/Project Name] - Technical Blueprint

## Business Context Reference

**PRD Reference**: [Link to PRD file - e.g., `artifacts/requirements/{feature-name}-prd.md`]

*For detailed business goals, scope, user stories, and success criteria, see the related PRD above.*

**Technical Focus**:
- This blueprint focuses on technical architecture and implementation strategy
- Business requirements and user workflows are documented in the PRD
- Blueprint translates business requirements into technical design

## Scope

**PRD Scope Reference**: See related PRD for complete functional scope

**Technical Scope** (what this blueprint covers):
- Major technical components to be built
- Architecture patterns and design decisions
- Integration points and interfaces
- Data models and storage strategy
- Non-functional requirements (performance, security, scalability)

### Technical Assumptions
- Technical capabilities and constraints
- Infrastructure and platform assumptions
- Technology stack assumptions

## Architecture Overview

**High-Level Architecture**:
- System architecture diagram (describe or reference)
- Major components and their relationships
- Data flow between components
- External system integrations

**Technology Stack**:
- Frontend technologies
- Backend technologies
- Database and data storage
- Infrastructure and deployment
- Third-party services and APIs

**Architectural Principles**:
- Key architectural decisions and rationale
- Design patterns to follow
- Constraints and trade-offs

## Major Components

### Component 1: [Component Name]

**Purpose**: What this component does and why it exists

**Responsibilities**:
- Key responsibilities
- Business logic it handles
- Data it manages

**Interfaces**:
- APIs it exposes
- Events it publishes/subscribes to
- Integration points

**Technology**:
- Implementation technology
- Key libraries or frameworks

**Scalability Considerations**:
- Expected load and scale
- Scaling approach

### Component 2: [Component Name]

[Repeat structure for each major component]

## Data Architecture

**Data Models**:
- Key entities and their relationships
- Data ownership and boundaries
- Schema design principles

**Data Flow**:
- How data moves through the system
- Data transformation points
- Data validation and integrity

**Data Storage**:
- Database choices and rationale
- Caching strategy
- Data retention and archival

**Data Security**:
- Sensitive data handling
- Encryption requirements
- Access control

## Integration Points

### Internal Integrations

**Component A ↔ Component B**:
- Integration mechanism (API, events, shared DB)
- Data exchanged
- Error handling

[Repeat for each integration]

### External Integrations

**External Service 1**:
- Purpose of integration
- API or protocol used
- Authentication/authorization
- Error handling and fallbacks
- Rate limits and quotas

[Repeat for each external integration]

## Technical Decisions

### Decision 1: [Decision Title]

**Context**: Why this decision is needed

**Options Considered**:
1. Option A: [Description, pros, cons]
2. Option B: [Description, pros, cons]
3. Option C: [Description, pros, cons]

**Decision**: Option chosen and why

**Consequences**: Implications of this decision

**ADR Reference**: [Link to ADR if created]

[Repeat for each major decision]

## Non-Functional Requirements

**Performance**:
- Response time requirements
- Throughput requirements
- Latency targets

**Scalability**:
- Expected scale (users, data volume, requests)
- Scaling approach (horizontal, vertical)
- Bottlenecks and mitigation

**Reliability**:
- Availability targets (SLA/SLO)
- Fault tolerance approach
- Disaster recovery

**Security**:
- Authentication and authorization
- Data encryption (at rest, in transit)
- Security compliance requirements
- Threat mitigation strategies

**Observability**:
- Logging strategy
- Monitoring and alerting
- Tracing and debugging

**Maintainability**:
- Code organization
- Testing strategy
- Documentation requirements

## Implementation Phases

### Phase 1: [Phase Name] (MVP/Foundation)

**Goals**: What this phase delivers

**Components**:
- Components to build in this phase
- Key features enabled

**Duration Estimate**: [Timeframe]

**Dependencies**: Prerequisites for this phase

**Deliverables**:
- What will be ready to use
- What will be tested and validated

### Phase 2: [Phase Name]

[Repeat structure for each phase]

## Risks and Mitigations

### Risk 1: [Risk Description]

**Impact**: High/Medium/Low
**Probability**: High/Medium/Low
**Mitigation Strategy**: How to address this risk
**Owner**: Who is responsible for managing this risk

[Repeat for each identified risk]

## Open Questions

- [Question 1 - needs clarification]
- [Question 2 - needs decision]
- [Question 3 - needs research]

## Dependencies

**External Dependencies**:
- Third-party services or APIs
- External team deliverables
- Infrastructure or platform requirements

**Internal Dependencies**:
- Other teams or projects
- Shared services or components
- Platform or tooling requirements

## Success Metrics

**Technical Metrics**:
- Performance benchmarks
- Availability targets
- Error rates

**Business Metrics**:
- User adoption metrics
- Business value indicators
- Feature usage metrics

## Related Documentation

- **PRD**: [Link to Product Requirements Document - e.g., `artifacts/requirements/{feature-name}-prd.md`]
- **HLD**: [Link to High-Level Design]
- **Mockups**: [Link to design files]
- **ADRs**: [Links to Architecture Decision Records]
- **Related Blueprints**: [Links to related blueprints]

**Note**: The PRD is the primary source for business goals, user stories, functional requirements, and success criteria. This blueprint focuses on technical architecture and implementation.
```

## Step 6: Fill in Blueprint Details

Based on gathered context, fill in each section:

**Business Context Reference**:
- If PRD exists, link to it: `artifacts/requirements/{feature-name}-prd.md`
- Note that blueprint focuses on technical design, PRD covers business requirements
- Extract high-level business context from PRD for reference

**Scope**:
- Reference PRD for functional scope
- Define technical scope (components, architecture, integrations)
- Document technical assumptions and constraints
- Note any technical limitations or trade-offs

**Architecture Overview**:
- Describe high-level system architecture
- Identify major components and their relationships
- Document technology choices with rationale
- Reference existing patterns and standards

**Major Components**:
- Break down system into logical components
- Define responsibilities and interfaces for each
- Consider scalability and performance
- Identify reusable vs. custom components

**Data Architecture**:
- Design key data models
- Define data flow through the system
- Choose appropriate storage solutions
- Address data security and compliance

**Integration Points**:
- Map all internal component integrations
- Document external service dependencies
- Define integration contracts
- Plan for error handling and resilience

**Technical Decisions**:
- Document key architectural decisions
- Present options and trade-offs considered
- Explain rationale for choices made
- Reference ADRs for significant decisions

**Non-Functional Requirements**:
- Extract from PRD or infer from scale
- Define performance targets
- Specify security and compliance needs
- Plan for observability and operations

**Implementation Phases**:
- Break delivery into logical phases
- Define MVP and incremental delivery
- Consider dependencies between phases
- Estimate rough timeline per phase

**Risks and Mitigations**:
- Identify technical and delivery risks
- Assess impact and probability
- Define mitigation strategies
- Assign ownership

## Step 7: Review and Refine

Present the blueprint and ask:

- "Does this blueprint capture the architectural vision?"
- "Are there any major components missing?"
- "Do the technical decisions make sense?"
- "Are the implementation phases realistic?"
- "Should I add more detail to any section?"

Make refinements based on feedback.

## Step 8: Determine Blueprint ID

**ID determination rules:**

1. **If PRD or project code exists**: Use the project code or initiative ID
   - Example: `[PROJECT-ID]`, `auth-system`, `reporting-v2`

2. **If Jira epic exists**: Use the epic key as base ID
   - Example: `PROJ-100` → `proj-100-auth-system`

3. **If no existing ID**: Create descriptive identifier
   - Format: `[short-initiative-name]`
   - Example: `user-onboarding`, `payment-integration`

**Short name guidelines:**
- Use kebab-case
- Keep it concise (2-4 words)
- Include key feature area
- Make it memorable and searchable

## Step 9: Save Blueprint

**Location**: All blueprints must be saved in the `artifacts/blueprints/` directory.

**Create directory if it doesn't exist**:
```bash
mkdir -p artifacts/blueprints/
```

**Determine directory and filename**:
- Each blueprint gets its own directory for organization
- Format: `artifacts/blueprints/{blueprint-id}--{short-name}/`
- Blueprint file: Always named `blueprint.md`
- Examples:
  - `artifacts/blueprints/auth--system/blueprint.md`
  - `artifacts/blueprints/proj-100--reporting-v2/blueprint.md`

**Save the file**:
- Full path: `artifacts/blueprints/{blueprint-id}--{short-name}/blueprint.md`
- Create the blueprint directory first

**Include metadata at the top**:
```markdown
---
created: YYYY-MM-DD
author: [Name]
id: [Blueprint ID]
related_prd: [Path to PRD file, e.g., artifacts/requirements/{feature-name}-prd.md]
related_hld: [HLD reference]
status: draft
---
```

**Note**: Always include the `related_prd` field if a PRD exists. This links the blueprint to its source requirements document.

**Final file structure**:
```
artifacts/blueprints/
├── README.md
├── auth--system/
│   ├── blueprint.md
│   └── tickets/           # Generated by /blueprint-to-tickets
├── proj-100--reporting-v2/
│   └── blueprint.md
└── progress--tracking/
    └── blueprint.md
```

## Step 10: Confirm Next Steps

After saving the blueprint:

1. **Display summary**:
   - Blueprint saved to: `artifacts/blueprints/{blueprint-id}--{short-name}/blueprint.md`
   - Number of major components identified
   - Number of implementation phases
   - Key technical decisions made

2. **Recommend next steps**:
   - "Blueprint is ready for review with your team"
   - "When approved, use `/blueprint-to-tickets` to decompose into Epics and tickets"
   - "Consider creating ADRs for major technical decisions in `artifacts/architecture/`"

3. **Ask for confirmation**:
   - "Is there anything else you'd like me to add or clarify in the blueprint?"
   - "Should I create ADRs for any of the technical decisions?"

## Best Practices

1. **Architecture-First**: Focus on system design, not implementation details
2. **Component-Based**: Break system into logical, loosely-coupled components
3. **Decision Documentation**: Document key decisions with rationale
4. **Scalability Focus**: Consider scale from the beginning
5. **Integration Design**: Pay attention to component and system boundaries
6. **Phased Delivery**: Plan for incremental delivery and value
7. **Risk Management**: Identify and plan for technical risks early
8. **Stakeholder Alignment**: Ensure blueprint addresses all stakeholder needs

## Guidelines

### Appropriate Level of Detail

**Include**:
- High-level architecture and component design
- Major technical decisions and rationale
- Integration patterns and contracts
- Non-functional requirements and targets
- Implementation phases and dependencies

**Don't Include**:
- Line-by-line implementation details (that's for `/spec`)
- Specific API endpoint schemas (unless defining contracts)
- Detailed test cases (that's for `/plan`)
- Code snippets (unless illustrating a pattern)

### When to Create a Blueprint

Create a blueprint when:
- Starting a significant new feature or initiative
- Making major architectural changes
- Integrating with new external systems
- Planning work that spans multiple epics
- Need to align team on technical approach

Don't create a blueprint for:
- Single ticket implementation
- Bug fixes or minor enhancements
- Changes within a single component
- Work already covered by existing blueprint

### Blueprint Lifecycle

1. **Draft**: Initial blueprint created, under review
2. **Approved**: Blueprint reviewed and approved by team
3. **In Progress**: Tickets generated, implementation started
4. **Completed**: All phases delivered
5. **Superseded**: Replaced by newer blueprint

Update blueprint status as initiative progresses.
