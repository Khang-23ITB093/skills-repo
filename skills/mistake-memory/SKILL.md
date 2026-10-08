---
name: mistake-memory
description: >-
  Self-learning mistake prevention system. Activate this skill when:
  (1) the user corrects a mistake or says "you already made this error before",
  (2) the agent detects it has repeated a known error pattern,
  (3) before writing code in a context that has recorded mistake patterns (XML, SQL, HTML, etc.),
  (4) during any code review or verification step to cross-check against known pitfalls.
  This skill maintains a persistent ledger of mistakes, performs deep root-cause analysis,
  generalizes errors to their full domain of related pitfalls, and enforces prevention
  checklists so the same class of error is never repeated.
---

# Mistake Memory — Self-Learning Error Prevention System

## Purpose

This skill acts as a **persistent, growing knowledge base of coding mistakes** that the
agent has made or been corrected on. It is not a static list — it is a living system that:

1. **Detects** when a mistake has occurred (user correction or self-detection)
2. **Analyzes** the root cause deeply, beyond the surface-level fix
3. **Generalizes** from the specific error to the entire family of related pitfalls
4. **Records** a structured entry with full context, related patterns, and prevention steps
5. **Applies** recorded knowledge proactively before writing any code in a matching context

The ledger file lives at: [ledger.md](./ledger.md)

---

## Core Principles

### Principle 1: Generalize, Don't Memorize
A single mistake reveals an entire **domain of related errors**.
- ❌ Only remembering `&` → `&amp;` in FXML
- ✅ Understanding that ALL XML special characters (`&`, `<`, `>`, `"`, `'`) must be
  escaped in ALL XML-based formats (`.xml`, `.fxml`, `.xhtml`, `.xsd`, `.pom.xml`)
- ✅ Further recognizing that **encoding/escaping rules** differ by context:
  XML entities, HTML entities, URL encoding, SQL parameterization, regex escaping,
  shell escaping, JSON string escaping, etc.

### Principle 2: Context-Aware Prevention
Each ledger entry specifies **where** and **when** it applies (file types, languages,
frameworks, specific code patterns). Before writing code, the agent must check if any
recorded entry matches the current context.

### Principle 3: Continuous Growth
The ledger is append-only. New entries are added; existing entries are updated with
additional examples or related patterns as they are discovered over time.

---

## Workflow: When a Mistake is Detected

Follow this exact procedure whenever a mistake is identified (by user or self-detected):

### Step 1: Acknowledge
- Acknowledge the error clearly without excessive apology
- State exactly what was wrong and what the correct approach is

### Step 2: Deep Analysis
Read the [Analysis Framework](./references/analysis-framework.md) and apply it:

1. **Surface Error**: What exactly was wrong? (the literal code mistake)
2. **Root Cause Domain**: What category/domain does this belong to?
   (e.g., "XML encoding", "SQL injection", "async/await semantics", "CSS specificity")
3. **Why It Happened**: What misconception or oversight led to the error?
4. **Complete Rule Set**: What are ALL the rules in this domain, not just the one that
   was violated? List every related rule exhaustively.
5. **Affected Contexts**: What file types, languages, frameworks, and code patterns
   does this apply to? Be comprehensive.
6. **Related Mistake Families**: What other common mistake domains are conceptually
   similar? (e.g., XML escaping → HTML escaping → URL encoding → all encoding contexts)

### Step 3: Check Existing Ledger
- Read [ledger.md](./ledger.md)
- Check if this mistake domain already has an entry
  - If yes: **Update** the existing entry with the new example and any missing rules
  - If no: **Create** a new entry following the ledger format below

### Step 4: Record to Ledger
Write or update the entry in [ledger.md](./ledger.md) using the format specified in
the Ledger Format section below.

### Step 5: Scan Current Codebase
After recording, immediately scan the current project for any other instances of the
same mistake class. Fix them proactively or report them to the user.

### Step 6: Verify Related Files
If the mistake was in a specific file, check all files of the same type in the project
for the same class of issues.

---

## Workflow: Before Writing Code (Proactive Prevention)

Before creating or modifying any file, the agent MUST:

1. **Read the ledger** at [ledger.md](./ledger.md)
2. **Identify matching entries** based on:
   - File type being edited (e.g., `.fxml` → check XML-related entries)
   - Language being used (e.g., Java → check Java-related entries)
   - Framework context (e.g., JavaFX → check JavaFX entries)
   - Code pattern being written (e.g., string concatenation in SQL → check SQL entries)
3. **Apply all matching prevention checklists** before finalizing the code
4. **Self-review** the output against each applicable entry's "Common Violations" list

---

## Ledger Format

Each entry in [ledger.md](./ledger.md) MUST follow this structure:

```markdown
## [ERR-NNN] <Concise Domain Title>

- **First Detected**: <date>
- **Last Updated**: <date>
- **Occurrences**: <count of times this error class was encountered>
- **Trigger**: <how it was detected: "User correction" | "Self-detected" | "Code review">
- **Severity**: <Critical | High | Medium | Low>

### Surface Error
<What exactly was wrong — with concrete code example>

### Root Cause Domain
<The broader category this belongs to>

### Complete Rule Set
<ALL rules in this domain, not just the violated one. Be exhaustive.>

### Affected Contexts
<File types, languages, frameworks, patterns where this applies>

### Common Violations (Anti-patterns)
<List of specific code patterns that violate these rules — things to watch for>

### Correct Patterns
<The correct way to write code in each violation scenario>

### Related Domains
<Other mistake families that share conceptual similarity>

### Prevention Checklist
<Concrete verification steps to run before/after writing code in this context>
```

---

## Self-Detection Triggers

The agent should proactively activate this skill when it notices:

1. **Writing code in a sensitive context**: XML, SQL queries, HTML templates, regex,
   shell commands, file paths, URL construction, serialization
2. **Pattern repetition**: If the agent catches itself about to write something it has
   corrected before
3. **User frustration signals**: Phrases like "I told you already", "again?",
   "you keep doing this", "same mistake", "didn't I say..."
4. **Code review moments**: Before committing, before presenting code to user,
   before running tests

---

## Important Notes

- The ledger file path is: `ledger.md` (trong thư mục skill) hoặc `~/.gemini/config/skills/mistake-memory/ledger.md`
- Entries apply across projects
- Never delete entries from the ledger; only add or update
- When updating an entry, always increment the occurrence count and update the date
- If the ledger file doesn't exist, create it with the header from the template
