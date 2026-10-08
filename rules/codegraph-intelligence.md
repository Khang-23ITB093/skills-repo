# Global Rule: CodeGraph-First Intelligence & Token Optimization

This environment utilizes **CodeGraph** to provide 100% local semantic code intelligence, conserve context tokens, and avoid duplicating existing codebase logic.

## 1. Zero Code Duplication (Check Before Writing)
- **Always verify existing symbols first**: Before writing a new helper function, repository query, utility method, model class, or network message handler, you **MUST** query CodeGraph to see if a similar method or class already exists.
- **Reuse existing patterns**: If an existing method performs the required logic or can be safely extended, reuse it instead of creating duplicate or competing implementations.

## 2. Token-Efficient Code Navigation
- **Do not blindly read whole files**: Avoid using `view_file` on large files (e.g. 200+ lines) or `grep_search` across entire directories when looking for definitions or usages.
- **Surgical Inspection**:
  - Use `codegraph explore <query>` or MCP tool `codegraph_explore` (server: `codegraph`) as the primary investigation step.
  - Use `codegraph node <symbol>` to view the exact outline, member signatures, and line numbers of a class/method.
  - Use `codegraph callers <symbol>` and `codegraph callees <symbol>` to trace call paths.
  - Read only the specific target lines needed using `view_file` with `StartLine` and `EndLine`.

## 3. Pre-Refactoring Blast Radius Analysis
- **Check impact before modifications**: Before renaming, refactoring, changing method signatures, or deleting code, run:
  `codegraph impact <symbol>`
  to identify all downstream classes, methods, and handlers that depend on it.

## 4. Index Maintenance
- In projects with a `.codegraph/` directory, after making code changes that add or modify classes/methods, run `codegraph sync` to keep the local graph database in sync.
