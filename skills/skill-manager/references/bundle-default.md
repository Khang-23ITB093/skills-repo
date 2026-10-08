# Default bundle (install when the user says "cài bộ mặc định" or lists these groups)

Order matters: finish and smoke test one group before the next. For every skill follow SKILL.md section 3 (clone, audit, license, copy to `_external/`, link by scope, record in lock + registry).

## Group 1 - Reports (scope: GLOBAL, install first)
Source: https://github.com/anthropics/skills (folder `skills/<name>`)

| Skill | Use | Smoke test |
|---|---|---|
| docx | Create/edit Word reports | open a sample .docx, list headings |
| pptx | Make/edit slides | open a sample .pptx, list slide titles |
| pdf | Read/extract PDFs, tables, forms | extract text from a sample PDF |
| xlsx | Spreadsheets, result tables, charts | open a sample .xlsx, list sheets |

Licence note: these four are source-available, not open source. Keep them in `_external/` (gitignored); do not commit copies. Dependencies (Python/Node packages, pandoc, LibreOffice...) are named in each SKILL.md: install what is listed, report what you added.

Optional CLI form (verify where it writes, then move/link): `npx skills add anthropics/skills@docx` (same for pptx, pdf, xlsx).

## Group 2 - Code (superpowers = PROJECT scope, skill-creator = GLOBAL)
- `skill-creator`: https://github.com/anthropics/skills (folder `skills/skill-creator`). Global.
- `superpowers`: https://github.com/obra/superpowers. Download into `_external/`, but do NOT link globally: it forces a plan/test/review process, so enable it per code project on request. Read its README for how it expects to be installed for Antigravity/Gemini-style agents; if it ships a `skills/` folder, copy those skill folders flat, keeping its license file.

Optional CLI form: `npx skills add obra/superpowers`, `npx skills add anthropics/skills@skill-creator`.

## Group 3 - Optional (PROJECT scope; download to library, do not link globally)
- `frontend-design`: https://github.com/anthropics/skills (folder `skills/frontend-design`). Enable only in web/UI projects.
- `addyosmani/agent-skills`: https://github.com/addyosmani/agent-skills. Inspect its structure first, list the skills it contains, install all of them into `_external/`, and enable per project on request. Do not link them globally.

## Final report to the user
One table: skill, group, scope, linked at (or "library only"), license, smoke test result, dependencies added, and anything the audit flagged. Then remind the user: external skills are gitignored and recorded in `skills.lock.md`; ask whether to commit and push the lock file.
