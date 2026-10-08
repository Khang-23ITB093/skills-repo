# Project Initialization Routine

This rule governs the mandatory behavior of the Antigravity Agent when entering a new workspace or project for the first time.

## 1. Project Analysis & Scaffold Check
When you start a new conversation in a project, immediately check if the `.agents/` directory and `AGENTS.md` exist in the workspace root.
If they do not exist, you MUST perform a "Project Initialization Routine":

1. **Scaffold Directory & Files**:
   - Create `AGENTS.md` at the workspace root defining core workspace rules (CodeGraph pre-action checks, Git clean workflow, model orchestration).
   - Create `.agents/rules/`
   - `.agents/skills/`

## 2. Capability & Tech Stack Analysis
Analyze the project's technology stack (e.g., look for `pom.xml`, `package.json`, `build.gradle`, `requirements.txt`, etc.).
Based on this analysis, determine which of the globally available rules and skills (located in `~/.gemini/config/`) would be beneficial for the current project.

## 3. Skill & Rule Synchronization
- **Auto-Sync / Suggestion**: Either automatically copy the relevant global rules and skills into the project's `.agents/` directory, OR proactively ask the user: "I notice this is a new project. I have created `AGENTS.md` and the `.agents/` directory. Would you like me to analyze the project and import relevant skills and rules, or do you have specific ones in mind?"
- **Git Hygiene**: Ensure `.agents/` is added to the project's `.gitignore` if version control is being used.

Always ensure the project has the necessary context (rules and skills) to maximize the effectiveness of the AI agents working on it.
