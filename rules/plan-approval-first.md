# Plan Approval Gate Rule

## MANDATORY — Always-On Directive for All Projects

Whenever the user requests a new feature, bug fix, architectural change, code refactoring, or multi-step technical implementation, you MUST enforce a **Plan-First Approval Gate** before taking any implementation actions.

---

## 1. Plan First, Do Not Execute
- **Artifact Creation**: Outline the full implementation plan in a structured plan artifact (with `RequestFeedback: true`).
- **Plan Requirements**:
  - Clear diagnosis or objective.
  - Step-by-step breakdown of actions.
  - Exact list of files to create, edit, or delete.
  - Verification & testing strategy.
- **STOP & WAIT**: Immediately halt after presenting the plan.
- **NO PROACTIVE EXECUTION**: You are strictly prohibited from writing code, editing files, creating new files, or executing state-altering commands in the same turn the plan is proposed.

---

## 2. Explicit User Approval Requirement
- You may only begin execution when the user:
  1. Clicks the **Proceed** button on the plan artifact, OR
  2. Gives clear, explicit approval in chat. Use one fixed keyword set everywhere —
     `duyệt`, `ok`, `làm đi`, `approve`, `lgtm`, `proceed`, `go ahead` — and when the `project-charter`
     skill recorded a different set for this project (its Q4.3 answer), that set wins.
     "Tiến hành đi", "Approved" and "Go ahead" count through those keywords; a bare "chắc là ổn" does not.
- If the user provides feedback, critiques, or asks for adjustments:
  - Revise the plan artifact accordingly.
  - Summarize key changes.
  - Stop and wait for approval on the revised plan.

---

## 3. Scope Exceptions
The planning gate applies to code and configuration changes. It does not apply to:
- Direct informational questions or explanations (e.g., "Giải thích đoạn code này", "Setting ở đâu?").
- Simple read-only inspections when the user asked for analysis only.
- Specific instructions where the user explicitly tells you to execute immediately (e.g., "Làm luôn không cần plan").
