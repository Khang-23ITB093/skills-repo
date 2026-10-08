# Global Rule: Multi-Model Orchestration & Workflow

This workspace uses the `multi-model-orchestration` skill for all task planning and model assignment decisions across all projects.

## Before Starting Any Significant Task
1. Read/activate the skill at `skills/multi-model-orchestration/SKILL.md`.
2. Classify the task using the Task Classification Schema.
3. Route to the appropriate model per the Routing Rules.
4. Apply the Escalation Policy for high-risk tasks.
5. Use Cross-Model Review for important deliverables.

## Available Models (Quick Reference)

| Model                         | Tier       | Best For                              |
|-------------------------------|------------|---------------------------------------|
| Gemini 3.8 Flash              | Workhorse  | Standard implementation, boilerplate  |
| Gemini 3.7 Flash              | Workhorse  | Parallel tasks, overflow              |
| Gemini 3.6 Flash              | Economy    | Trivial tasks, docs, comments         |
| Gemini 3.1 Pro                | Premium    | Architecture, algorithms              |
| Claude Sonnet 4.6 (Thinking)  | Premium    | Code review, security, concurrency    |
| Claude Opus 4.6 (Thinking)    | Elite      | Critical decisions, tie-breaking      |
| GPT-OSS 120B (Medium)         | Premium    | Second opinions, structured reasoning |

## General Rules
- Always classify tasks before assigning to a model.
- Never use Elite/Premium models for boilerplate or CRUD.
- Cross-model review is mandatory for architecture decisions.
- Check quota regularly with `agy usage` and update the model registry.
- Maintain task status in `.agents/PROGRESS.md` or active implementation plans.
- Commit working subtasks to Git immediately after verification.
- On restart or session resume: check `git status` + `.agents/PROGRESS.md` to resume active work without re-planning.
