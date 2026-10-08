# Git layout for the skills repo

```
<skills-repo>/
├── skill-manager/            # own, committed
├── <other-own-skill>/        # own, committed
├── _external/                # third-party copies, NEVER committed
├── skills.lock.md            # committed manifest of external skills
├── REGISTRY.md               # committed (no personal absolute paths)
├── INSTALL.md                # committed: how others set this up
└── .gitignore
```
## Git layout suggestions

```
skills-repo/
├── .gitignore            # _external/, scratch/, ledger thật, .env
├── LICENSE
├── README.md             # cho người đọc
├── AGENTS.md             # cho agent
├── INSTALL.md
├── REGISTRY.md
├── skills.lock.md        # danh sách skill ngoài (commit)
├── scripts/
│   ├── sync.ps1
│   └── sync.sh
├── docs/                 # PROJECT.md, audits tiêu biểu
├── rules/                # kebab-case, ngắn, trỏ tới skill
│   ├── model-routing.md  # gộp 3 rule
│   ├── codegraph-intelligence.md
│   ├── git-author-clean-code.md
│   ├── destructive-operations-safety.md
│   ├── plan-approval-first.md
│   └── project-initialization.md
├── skills/               # chỉ skill của bạn, phẳng
│   ├── anthropic-agent-guide/
│   ├── codegraph/
│   ├── git-clean-workflow/
│   ├── mistake-memory/   # ledger.example.md
│   ├── multi-model-orchestration/
│   ├── orimise-deep-planning/  # + tests/
│   ├── playwright/       # nếu tự viết
│   └── skill-manager/    # + references/
├── _external/            # gitignored
└── scratch/              # gitignored
```
## .gitignore
```
_external/
.env
*.key
*.pem
__pycache__/
node_modules/
```
If SKILLS_HOME is also the directory Antigravity scans and externals are installed flat, add each external skill name (one per line) to `.gitignore` too.

## skills.lock.md
```
# External skills (reinstall with the skill-manager skill)

| Skill | Source repo | Path in repo | Commit | License | Scope | Installed |
|---|---|---|---|---|---|---|
| docx | https://github.com/anthropics/skills | skills/docx | <sha> | source-available | global | YYYY-MM-DD |
```

## INSTALL.md (for other people)
1. Clone this repo.
2. Copy or link the own skills into your Antigravity skills directory.
3. Ask Antigravity: "Use skill-manager. Install every external skill listed in skills.lock.md at the scope given there."
4. Read each external skill's license before using it commercially.
