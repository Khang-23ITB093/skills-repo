# Mistake Ledger

> Persistent knowledge base of coding mistakes. Each entry represents a **domain of errors**,
> not a single instance. Entries are append-only: never delete, only add or update.
>
> This ledger is automatically consulted before writing code in any matching context.

---

## [ERR-001] XML/FXML Special Character Escaping

- **First Detected**: 2026-09-21
- **Last Updated**: 2026-09-21
- **Occurrences**: 1
- **Trigger**: User correction
- **Severity**: Critical

### Surface Error
Used raw `&` character in a JavaFX FXML file attribute value, causing XML parse failure.

```xml
<!-- ❌ WRONG — causes SAXParseException / LoadException -->
<Button text="Download & Watch" />

<!-- ✅ CORRECT -->
<Button text="Download &amp; Watch" />
```

### Root Cause Domain
**Encoding & Escaping → XML Entity Encoding**

XML is a strict markup language where certain characters have special meaning in the
parser. Using them as literal text without proper escaping makes the document
malformed (not well-formed XML), causing immediate parse failure at runtime.

### Complete Rule Set

All XML special characters that MUST be escaped:

| Character | Entity | Required In | Notes |
|-----------|--------|-------------|-------|
| `&` | `&amp;` | Content + Attributes | Always required. Most common mistake. |
| `<` | `&lt;` | Content + Attributes | Always required. Conflicts with tag opening. |
| `>` | `&gt;` | Content (best practice) | Technically optional in some positions, but always escape. |
| `"` | `&quot;` | Attribute values (double-quoted) | Required when attribute uses `"..."` delimiters. |
| `'` | `&apos;` | Attribute values (single-quoted) | Required when attribute uses `'...'` delimiters. |

Additional XML rules:
- Comments (`<!-- -->`) cannot contain `--` inside the body
- Processing instructions (`<?...?>`) cannot contain `?>`
- CDATA sections (`<![CDATA[...]]>`) cannot contain `]]>`
- Numeric character references: `&#NNN;` (decimal) or `&#xHHH;` (hex) for any Unicode character

### Affected Contexts

| File Extension | Format | Framework/Tool |
|---------------|--------|---------------|
| `.fxml` | JavaFX FXML | JavaFX |
| `.xml` | Generic XML | Any |
| `.xhtml` | XHTML | Web |
| `.xsd` | XML Schema | Validation |
| `.xsl` / `.xslt` | XSLT | Transformation |
| `.pom` / `pom.xml` | Maven POM | Build |
| `.svg` | SVG Graphics | Graphics |
| `.wsdl` | Web Services | SOAP |
| `.rss` / `.atom` | Feed Formats | Syndication |
| `.jsp` | JavaServer Pages | Java EE (XML parts) |
| Android `*.xml` | Layouts, Strings, etc. | Android SDK |
| Spring `*.xml` | Bean configs | Spring Framework |

### Common Violations (Anti-patterns)

```xml
<!-- ❌ Raw & in text -->
<Label text="Terms & Conditions"/>

<!-- ❌ Raw & in attribute with special chars -->
<TextField promptText="Search: name & age"/>

<!-- ❌ Comparison operators used literally -->
<Label text="x < 10"/>

<!-- ❌ Quotes inside quotes -->
<Label text="He said "hello""/>
```

### Correct Patterns

```xml
<!-- ✅ Escaped & -->
<Label text="Terms &amp; Conditions"/>

<!-- ✅ Escaped & in attribute -->
<TextField promptText="Search: name &amp; age"/>

<!-- ✅ Escaped < -->
<Label text="x &lt; 10"/>

<!-- ✅ Escaped quotes -->
<Label text="He said &quot;hello&quot;"/>
```

### Related Domains

- **HTML Entity Encoding**: Similar but more permissive (`&amp;`, `&lt;`, `&gt;`,
  `&quot;`, plus named entities like `&nbsp;`, `&copy;`)
- **URL Encoding (Percent-Encoding)**: `%20` for space, `%26` for `&`, `%3D` for `=`
- **JSON String Escaping**: `\"`, `\\`, `\n`, `\t`, `\uNNNN`
- **SQL Parameterization**: Never concatenate user input — use prepared statements
- **Shell Escaping**: Quoting rules for bash/PowerShell arguments
- **Regex Escaping**: `\.`, `\*`, `\+`, `\?`, `\(`, `\)`, etc.

### Prevention Checklist

- [ ] After writing/modifying ANY XML-based file, scan all attribute values and text
      content for raw `&`, `<`, `>`, `"` characters
- [ ] When inserting dynamic or user-provided text into XML, use the framework's
      built-in XML escaping utility (never raw string concatenation)
- [ ] If the file contains text with natural language (labels, buttons, messages),
      pay extra attention to ampersands in phrases like "X & Y"
- [ ] Verify the file is well-formed XML by checking for IDE validation errors
- [ ] When copy-pasting text from non-XML sources into XML files, always review for
      characters that need escaping

---

*— End of current ledger entries —*
