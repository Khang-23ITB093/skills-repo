# Deep Analysis Framework for Mistake Classification

This document provides the structured thinking process for analyzing a coding mistake
beyond its surface-level fix. Use this when recording a new entry in the ledger.

---

## Step 1: Identify the Surface Error

Ask: **"What exactly was wrong in the code?"**

Document:
- The exact line(s) of code that were incorrect
- The exact correction that was applied
- The error message or symptom (if applicable)

---

## Step 2: Classify the Root Cause Domain

Ask: **"What fundamental concept or rule was violated?"**

Common domains (not exhaustive):

| Domain | Examples |
|--------|----------|
| **Encoding & Escaping** | XML entities, HTML entities, URL encoding, SQL parameterization, JSON escaping, regex escaping, shell escaping, base64 |
| **Type System & Casting** | Null safety, type coercion, generics misuse, autoboxing pitfalls |
| **Concurrency & Threading** | Race conditions, deadlocks, thread safety, atomic operations, volatile |
| **Resource Management** | Unclosed streams, connection leaks, memory leaks, missing finally/try-with-resources |
| **API Contract** | Wrong method signature, incorrect parameter order, deprecated API, version mismatch |
| **Data Validation** | Missing null checks, boundary conditions, empty collections, invalid state |
| **Path & Environment** | OS-specific paths, case sensitivity, file separators, encoding, line endings |
| **Security** | Injection (SQL, XSS, command), hardcoded secrets, insecure defaults |
| **Syntax & Format** | Language-specific syntax, file format rules (XML well-formedness, JSON syntax) |
| **Logic & Semantics** | Off-by-one, operator precedence, short-circuit evaluation, equality vs identity |
| **Framework Conventions** | Framework-specific lifecycle, annotations, naming conventions, dependency injection |
| **Build & Dependencies** | Version conflicts, missing dependencies, incorrect scope, classpath issues |

---

## Step 3: Exhaustive Rule Enumeration

Ask: **"What are ALL the rules in this domain, not just the one I violated?"**

This is the most critical step. For every domain, there is a **complete set of rules**.
You must enumerate ALL of them, not just the one that triggered the error.

### Example: XML Encoding Domain

If the mistake was `&` → `&amp;`, the COMPLETE rule set is:

| Character | Entity | Where Required |
|-----------|--------|----------------|
| `&` | `&amp;` | Everywhere in XML content and attributes |
| `<` | `&lt;` | Everywhere in XML content and attributes |
| `>` | `&gt;` | In content (technically optional but best practice) |
| `"` | `&quot;` | Inside attribute values delimited by double quotes |
| `'` | `&apos;` | Inside attribute values delimited by single quotes |

Additionally: CDATA sections (`<![CDATA[...]]>`) can wrap raw text,
processing instructions have their own rules, comments cannot contain `--`, etc.

---

## Step 4: Map Affected Contexts

Ask: **"Where does this rule apply? What file types, languages, and scenarios?"**

Be comprehensive. For XML encoding, this affects:
- `.xml` (generic XML)
- `.fxml` (JavaFX)
- `.xhtml` (XHTML)
- `.xsd` (XML Schema)
- `.xsl` / `.xslt` (XSLT stylesheets)
- `.wsdl` (Web Services)
- `.pom` / `pom.xml` (Maven)
- `.svg` (Scalable Vector Graphics)
- `.rss` / `.atom` (Feed formats)
- Any XML-based configuration format (Spring, Android layouts, etc.)

---

## Step 5: Identify Related Mistake Families

Ask: **"What other mistake domains share the same conceptual pattern?"**

This helps build cross-domain awareness. Examples:

- XML escaping ↔ HTML escaping ↔ URL encoding ↔ JSON escaping
  → All belong to **"context-specific encoding"**
  
- SQL injection ↔ Command injection ↔ XSS ↔ Path traversal
  → All belong to **"untrusted input handling"**

- Unclosed streams ↔ Connection leaks ↔ Unreleased locks
  → All belong to **"resource lifecycle management"**

---

## Step 6: Create Prevention Checklist

Ask: **"What concrete steps can I take before and after writing code to prevent this?"**

A good checklist is:
1. **Specific** — not "be careful" but "check every `&` character in attribute values"
2. **Actionable** — can be mechanically verified
3. **Contextual** — triggered by file type, language, or code pattern

Example for XML encoding:
- [ ] Before saving any `.fxml`/`.xml` file, scan all text content and attribute values
- [ ] Verify no raw `&`, `<`, `>` characters exist outside of entity references or CDATA
- [ ] If inserting user-provided text into XML, use a proper XML builder/escaper utility
- [ ] Run XML well-formedness check (IDE validation or `xmllint`)

---

## Step 7: Rate Severity

| Severity | Criteria |
|----------|----------|
| **Critical** | Causes runtime crash, data loss, or security vulnerability |
| **High** | Causes build failure or incorrect behavior that is hard to diagnose |
| **Medium** | Causes minor incorrect behavior or cosmetic issues |
| **Low** | Style/convention violation with no functional impact |
