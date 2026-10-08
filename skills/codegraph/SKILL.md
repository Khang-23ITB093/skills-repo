---
name: codegraph
description: >
  Semantic code intelligence, caller/callee analysis, impact tracing, and symbol navigation
  using CodeGraph (100% local, pre-indexed knowledge graph). Use during reasoning to conserve
  tokens, avoid duplicating existing methods, and verify blast radius before refactoring.
---

# CodeGraph Intelligence & Anti-Duplication Skill

## Purpose
This skill establishes an AI reasoning protocol that uses **CodeGraph** to:
1. **Conserve tokens**: Surgical inspection instead of dumping entire files into context.
2. **Prevent duplication**: Never re-create or invent methods/classes that already exist in the codebase.
3. **Prevent regressions**: Check downstream dependencies (blast radius) before modifying or deleting code.

---

## 1. The CodeGraph Thinking Protocol

Whenever planning a code change or answering structural questions, follow this 4-step sequence:

### Step 1: Symbol & Method Existence Check (Anti-Duplication)
*Problem: AI agents frequently write new helper methods or duplicate existing DB queries because they haven't seen the whole codebase.*
- **Action**: Run `codegraph query <keyword>` or `codegraph node <TargetClass>` to check if a method already exists.
- **Example**: Before writing a method to find user by ID or check group membership in `GroupRepo`:
  ```powershell
  codegraph node GroupRepo
  # or search for symbol
  codegraph query findUser
  ```
- **Rule**: If a method exists, **REUSE IT**. Never create redundant methods like `fetchGroupById` if `getGroup` or `findGroup` already exists.

### Step 2: Caller & Callee Analysis
*Problem: Guessing how data flows across layers (Controller → Service → Repo) wastes context tokens.*
- **Action**:
  - `codegraph callers <method>`: See who calls this method.
  - `codegraph callees <method>`: See what other methods/APIs this method calls.
  - `codegraph explore "<feature_name>"`: Trace the end-to-end call path for a feature.

### Step 3: Blast Radius / Impact Verification
*Problem: Changing a method signature or return type can break callers in other files without the AI noticing.*
- **Action**: Before modifying any shared method, model, or interface, run:
  ```powershell
  codegraph impact <method_name>
  ```
- **Review**: Inspect all affected symbols listed in the output. Update every caller accordingly in your implementation plan.

### Step 4: Surgical File Reading
*Problem: Reading 800 lines of code when only 20 lines are needed burns context tokens and degrades model attention.*
- **Action**: Use `codegraph node <symbol>` to find the exact line number (e.g. `createGroup:11`), then use `view_file` with precise `StartLine: 10, EndLine: 35`.

---

## 2. Command Reference

```powershell
# 1. Search for existing symbols (methods, classes, fields)
codegraph query <symbol_or_keyword>

# 2. Inspect a class or method outline + line numbers + callers
codegraph node <ClassName_or_MethodName>

# 3. Find all callers of a method
codegraph callers <method_name>

# 4. Find all methods called by a method
codegraph callees <method_name>

# 5. Check blast radius before refactoring/changing signatures
codegraph impact <method_name>

# 6. Explore end-to-end call flow of a feature
codegraph explore "<feature_query>"

# 7. Check index status
codegraph status

# 8. Sync index after creating or modifying files
codegraph sync
```

---

## 3. Maintenance Rule
Whenever new files, classes, or methods are added to the codebase during a task, run:
```powershell
codegraph sync
```
This ensures the local SQLite graph is immediately up-to-date for subsequent queries.
