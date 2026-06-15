---
name: generate-agents
description: Generates a customized AGENTS.md file from .claude/skills/generate-agents/AGENTS-template.md by extracting parameter values and replacing placeholders throughout the template.
---

## Description

Generates a customized `AGENTS.md` file from
`.claude/skills/generate-agents/AGENTS-template.md` by extracting parameter values and
replacing all placeholders throughout the template.

## Instructions

This skill should:

1. **Prompt user with instructions for filling out the template**
   - Display this informative message to the user:
     ```
     Before generating AGENTS.md, please ensure the following parameters are filled in .claude/skills/generate-agents/AGENTS-template.md:

     Critical Parameters that need to be filled in:
     - PROJECT_NAME: Your project name (e.g., "retail-data-demo")
     - PROJECT_KEY: Your Jira project key (e.g., "RETAIL")
     - TEAM_NAME: Your team name (e.g., "Engineering")
     - AUTHOR_NAME: Your name
     - PROJECT_DESCRIPTION: Brief description of your project
     - PROJECT_PURPOSE: The main purpose or business objective
     - REPO_URL: Your repository URL

     Instructions:
     1. Open .claude/skills/generate-agents/AGENTS-template.md
     2. Find the PARAMETERS SECTION (between <!-- PARAMETERS SECTION and END PARAMETERS -->)
     3. Replace each placeholder value with your actual project information
     4. Save the file

     Example:
     Change: PROJECT_NAME: [Your Project Name] (e.g., "test-genx-workflow")
     To:     PROJECT_NAME: retail-data-demo

     Would you like help filling out the template? (Type "yes" for assistance, or "no" to proceed)
     ```
   - Wait for user response:
     - If user wants help ("yes"/"y"): Ask questions to gather values for each parameter, then offer to update `.claude/skills/generate-agents/AGENTS-template.md` with the values
     - If user doesn't need help ("no"/"n") or after helping: Ask "Ready to proceed with generating AGENTS.md? (Type 'yes' to continue)"
     - If user says "yes" to proceed: Continue to step 2
     - If user says "no" or "cancel": Abort with message: "Generation cancelled. Please edit .claude/skills/generate-agents/AGENTS-template.md when ready."

2. **Read the template file**
   - Read `.claude/skills/generate-agents/AGENTS-template.md`
   - Verify the file exists and is readable

3. **Extract parameters**
   - Extract all parameter values from the PARAMETERS section (between `<!-- PARAMETERS SECTION` and `END PARAMETERS -->`)
   - Parse the parameters as key-value pairs (format: `KEY: value`)

4. **Replace placeholders**
   - Replace all placeholders in the template with actual values:
   - `[Project Name]` -> `PROJECT_NAME` value
   - `[Your Project Name]` -> `PROJECT_NAME` value
   - `[Brief description...]` -> `PROJECT_DESCRIPTION` value
   - `[Your Team Name]` -> `TEAM_NAME` value
   - `[PROJECT_KEY]` -> `PROJECT_KEY` value
   - `[YOUR_ORG]` -> `ATLASSIAN_ORG` value
   - `[BOARD_ID]` -> `JIRA_BOARD_ID` value
   - `[YOUR_CLOUD_ID]` -> `ATLASSIAN_CLOUD_ID` value
   - `[Your Name]` -> `AUTHOR_NAME` value
   - `[main/master/develop]` or `[main]` -> `DEFAULT_BRANCH` value
   - `[FRONTEND_PORT]` -> `FRONTEND_PORT` value
   - `[BACKEND_PORT]` -> `BACKEND_PORT` value
   - And all other parameter placeholders throughout the document

5. **Update Project structure section**
   - Update the Project structure section to align the current folder structure

6. **Remove PARAMETERS section**
   - Remove the entire PARAMETERS section from the output (from `<!-- PARAMETERS SECTION` through `END PARAMETERS -->`)

7. **Write output file**
   - Write the clean, customized content to `AGENTS.md` in the project root folder

## Output

Create `AGENTS.md` with:
- No PARAMETERS section
- All placeholders replaced with actual values
- Smart replacements applied for edge cases
- Clean, production-ready agent context file

## Error Handling

If `.claude/skills/generate-agents/AGENTS-template.md` is not found or PARAMETERS
section is missing/malformed:
- Display clear error message
- Explain what's needed
- Do not create/overwrite `AGENTS.md`
