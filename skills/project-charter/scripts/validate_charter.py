#!/usr/bin/env python3
"""Validate a Project Charter produced by the project-charter skill.

Portable: Python 3.7+ standard library only. No third-party dependencies.
Works on Windows, Linux and macOS. Console output is forced to UTF-8 so a
cp437/cp1252 Windows console cannot turn a PASS into a UnicodeEncodeError.

Usage:
    python3 validate_charter.py <project-root>
    python3 validate_charter.py <project-root> --claude   # require the Claude Code bridge + mirror
    python3 validate_charter.py <project-root> --json

Exit codes:
    0  all checks passed (warnings do not fail the gate)
    1  one or more checks failed
    2  bad invocation (project root missing)
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

AGENTS_MD_MAX_LINES = 100
AGENTS_MD_MAX_BYTES = 32 * 1024
RULE_MAX_BYTES = 24_000
ALWAYS_ON_MAX_LINES = 40
DAILY_SKILL_BUDGET = 10
# Always-on rule budget: Antigravity demotes the largest files past 20k tokens.
ALWAYS_ON_TOKEN_WARN = 3_000
ALWAYS_ON_TOKEN_FAIL = 20_000
BYTES_PER_TOKEN = 4

PORTABLE_FRONTMATTER = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
VALID_TRIGGERS = {"always_on", "model_decision", "glob", "manual"}
NON_PORTABLE_KEYS = {
    "disable-model-invocation",
    "user-invocable",
    "paths",
    "context",
    "agent",
    "background",
    "hooks",
    "model",
    "effort",
    "shell",
    "arguments",
    "argument-hint",
    "when_to_use",
    "disallowed-tools",
}

# Credential *assignments*. The lookbehind stops `OPENAI_API_KEY=` from slipping
# through on the `_` boundary, which the earlier \b version did.
CREDENTIAL_RE = re.compile(
    r"(?i)[A-Za-z0-9_]*(?:api[_-]?key|token|secret|passwd|password|pwd)\s*[:=]\s*"
    r"['\"]?([A-Za-z0-9_\-\.]{12,})"
)
# A value that is itself an identifier (DATABASE_PASSWORD) names a variable
# rather than leaking a secret, and the docs ask for exactly that style.
IDENTIFIER_ONLY_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")

SECRET_PATTERNS = [
    (r"\bsk-[A-Za-z0-9]{16,}", "OpenAI-style key"),
    (r"\bAIza[A-Za-z0-9_\-]{20,}", "Google API key"),
    (r"\bgh[pousr]_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}", "GitHub token"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r"(?i)\b(postgres|postgresql|mysql|mongodb|redis)://[^\s]+:[^\s]+@", "connection string with credentials"),
    (r"(?i)\bBearer\s+[A-Za-z0-9_\-\.]{20,}", "bearer token"),
]

# Any absolute path makes a committed file unportable. `env:NAME` is the only
# accepted way to name a machine-specific location.
ABS_PATH_PATTERNS = [
    (r"\b[A-Za-z]:[\\/](?![*<])", "absolute Windows path"),
    (r"\\\\[A-Za-z0-9._\-]+\\[A-Za-z0-9._$\-\\]+", "UNC network path"),
    (r"/(?:home|Users)/[A-Za-z0-9._\-]+/", "absolute home path"),
]

CHECK_COMMAND_RE = re.compile(r"`([^`\n]+)`")
FENCE_LINE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
SHELL_FENCE_LABELS = {"bash", "sh", "zsh", "shell", "console", "cmd", "powershell", "ps1", "pwsh"}
# `<...>`, `<…>` and `<placeholder>` are all template leftovers. The lookbehind
# keeps generic types (`List<String>`, `Promise<void>`) out of the report.
PLACEHOLDER_RE = re.compile(r"(?<![A-Za-z0-9_])<\.{2,}>|<\u2026>|(?<![A-Za-z0-9_])<[A-Za-z][^<>\n]{0,60}>")
# Claude-only substitutions: these are left as literal text by other hosts.
HOST_SPECIFIC_TOKENS = (r"\$\{CLAUDE_[A-Z_]+\}", r"\$ARGUMENTS")

OPTIONAL_DIRS = (".agents/skills", ".claude/skills")


def harden_stdout() -> None:
    """Force UTF-8 on the report streams (Python 3.7+ TextIOWrapper)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def iter_fences(text: str):
    """Yield (label, body_lines) for every fenced block, in order.

    Line-based on purpose: a regex cannot tell an opening fence from a closing
    one, so an "optional label" pattern let every closing fence open a capture
    that swallowed the prose after it — which then looked like an executable
    portability defect in a vendored skill nobody is allowed to edit.
    """
    label = None
    marker = ""
    body: list[str] = []
    for line in text.splitlines():
        match = FENCE_LINE_RE.match(line)
        if match and label is None:
            marker = match.group(2)
            raw = match.group(3).strip()
            label = raw.split()[0].lower() if raw else ""
            body = []
            continue
        if match and label is not None and match.group(2)[0] == marker[0] and len(match.group(2)) >= len(marker):
            yield label, body
            label = None
            marker = ""
            body = []
            continue
        if label is not None:
            body.append(line)
    if label is not None:  # unterminated fence: still its body
        yield label, body


def executable_fences(text: str) -> str:
    """Concatenate the bodies of fences that an agent would execute.

    Shell-labelled fences and bare fences (which in practice hold commands) are
    collected; language blocks such as ```yaml or ```markdown are documentation,
    so a `${CLAUDE_SKILL_DIR}` mentioned there is not a defect.
    """
    return "\n".join(
        "\n".join(body) for label, body in iter_fences(text)
        if label in SHELL_FENCE_LABELS or label == ""
    )


def strip_fences(text: str) -> str:
    """Text outside any fence, for prose-only scans."""
    kept: list[str] = []
    inside = False
    for line in text.splitlines():
        if FENCE_LINE_RE.match(line):
            inside = not inside
            continue
        if not inside:
            kept.append(line)
    return "\n".join(kept)


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def add(self, check: str, ok: bool, detail: str = "") -> None:
        self.rows.append((check, "PASS" if ok else "FAIL", detail))

    def warn(self, check: str, detail: str) -> None:
        self.rows.append((check, "WARN", detail))

    def skip(self, check: str, detail: str) -> None:
        self.rows.append((check, "SKIP", detail))

    @property
    def failed(self) -> bool:
        return any(status == "FAIL" for _, status, _ in self.rows)

    def render(self) -> str:
        width = max((len(c) for c, _, _ in self.rows), default=10)
        lines = []
        for check, status, detail in self.rows:
            suffix = f"  - {detail}" if detail else ""
            lines.append(f"{status:<5} {check:<{width}}{suffix}")
        return "\n".join(lines)


def read_text(path: str) -> str:
    # utf-8-sig strips a leading BOM: PowerShell 5.1's `-Encoding UTF8` writes one,
    # and an unhandled BOM would break frontmatter and first-line detection.
    with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
        return handle.read()


def parse_frontmatter(text: str) -> tuple[dict[str, list[str]], bool]:
    """Return (key -> value lines, has_frontmatter).

    A key's value lines exclude the key name itself: an inline value is one line,
    a block scalar (`>-`, `|`) contributes its indented body. "Is the field
    filled" is therefore a non-empty join, not a guess at the scalar style.
    """
    if not text.startswith("---"):
        return {}, False
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, False
    values: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines[1:]:
        if line.strip() == "---":
            return values, True
        match = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)$", line)
        if match:
            current = match.group(1)
            inline = match.group(2).strip()
            values[current] = [] if inline in (">-", ">", "|", "|-", ">+", "|+") else [inline]
            continue
        if current is not None and line.startswith((" ", "\t")):
            values[current].append(line.strip())
        elif line.strip():
            current = None
    return values, False  # unterminated frontmatter


def field_text(values: dict[str, list[str]], key: str) -> str:
    return " ".join(part for part in values.get(key, []) if part).strip()


def normalise_scalar(value: str) -> str:
    """Strip quotes and a trailing `# comment` from a one-line frontmatter value."""
    text = value.strip()
    text = re.split(r"\s+#", text, maxsplit=1)[0].strip()
    return text.strip("'\"")


def collect_charter_files(root: str) -> list[str]:
    """Committed charter files (the scope of the secrets / absolute-path scan).

    The manifest and the registry are committed too, so they are scanned: they
    are exactly where a machine path used to leak.
    """
    targets = [
        os.path.join(root, "AGENTS.md"),
        os.path.join(root, "CLAUDE.md"),
        os.path.join(root, ".agents", "context"),
        os.path.join(root, ".agents", "rules"),
        os.path.join(root, ".agents", "skills.manifest.json"),
        os.path.join(root, ".agents", "skills", "REGISTRY.md"),
    ]
    found: list[str] = []
    for target in targets:
        if os.path.isfile(target):
            found.append(target)
        elif os.path.isdir(target):
            for dirpath, _dirnames, filenames in os.walk(target):
                for name in filenames:
                    if name.lower().endswith((".md", ".json", ".yaml", ".yml")):
                        found.append(os.path.join(dirpath, name))
    return found


def check_agents_md(root: str, report: Report) -> str:
    path = os.path.join(root, "AGENTS.md")
    if not os.path.isfile(path):
        report.add("AGENTS.md exists", False, "missing at project root")
        return ""
    text = read_text(path)
    size = os.path.getsize(path)
    # splitlines() counts real lines: `count("\n") + 1` reported a 100-line file
    # that ends with a newline as 101 and failed a correct charter.
    lines = len(text.splitlines())

    report.add(
        "AGENTS.md size",
        lines <= AGENTS_MD_MAX_LINES and size <= AGENTS_MD_MAX_BYTES,
        f"{lines} lines, {size} bytes (limits {AGENTS_MD_MAX_LINES} lines / {AGENTS_MD_MAX_BYTES} bytes)",
    )
    has_frontmatter = text.lstrip().startswith("---")
    report.add("AGENTS.md has no frontmatter", not has_frontmatter,
               "starts with '---'" if has_frontmatter else "")
    first = next((line.strip() for line in text.splitlines() if line.strip()), "")
    report.add("AGENTS.md starts with a heading", first.startswith("#"),
               f"first content line is {first[:40]!r}" if not first.startswith("#") else "")
    return text


def check_claude_bridge(root: str, require: bool, report: Report) -> None:
    claude_path = os.path.join(root, "CLAUDE.md")
    local_path = os.path.join(root, "CLAUDE.local.md")

    if os.path.islink(claude_path):
        report.add("CLAUDE.md is a real file (not symlink)", False,
                   "Edit/Write refuse to write through symlinks and Windows clones break them")
    elif os.path.isfile(claude_path):
        text = read_text(claude_path)
        # The contract is exactly the import line: extra commentary drifts and
        # every host reads the import anyway.
        report.add("CLAUDE.md is exactly '@AGENTS.md'", text.strip() == "@AGENTS.md",
                   "" if text.strip() == "@AGENTS.md"
                   else "content must be the single line '@AGENTS.md'")
    elif require:
        report.add("CLAUDE.md exists (Claude Code target)", False, "required but missing")
    else:
        report.warn("CLAUDE.md", "absent - fine unless Claude Code is a target host")

    if os.path.isfile(local_path):
        report.add("No CLAUDE.local.md", False,
                   "its presence suppresses AGENTS.md for Claude Code by default")


def check_rules(root: str, report: Report) -> None:
    rules_dir = os.path.join(root, ".agents", "rules")
    if not os.path.isdir(rules_dir):
        report.add(".agents/rules/ exists", False, "missing")
        return

    nested = [d for d in os.listdir(rules_dir) if os.path.isdir(os.path.join(rules_dir, d))]
    report.add(".agents/rules/ is flat", not nested,
               f"nested dirs ignored by Antigravity: {', '.join(nested)}" if nested else "")

    files = sorted(f for f in os.listdir(rules_dir) if f.lower().endswith(".md"))
    report.add(".agents/rules/ has rule files", bool(files), f"{len(files)} file(s)")
    if not files:
        return

    oversized, bad_frontmatter, bad_trigger, non_portable = [], [], [], []
    always_on_bytes = 0
    long_always_on, missing_trigger = [], []
    for name in files:
        path = os.path.join(rules_dir, name)
        text = read_text(path)
        size = os.path.getsize(path)
        if size > RULE_MAX_BYTES:
            oversized.append(name)
        values, closed = parse_frontmatter(text)
        if (not closed or not field_text(values, "name")
                or not field_text(values, "description")):
            bad_frontmatter.append(name)
            continue
        trigger = normalise_scalar(field_text(values, "trigger"))
        if trigger and trigger not in VALID_TRIGGERS:
            bad_trigger.append(f"{name}:{trigger}")
        if not trigger:
            missing_trigger.append(name)
        # A rule without an explicit trigger is always-on in practice, so it
        # counts against Antigravity's budget too.
        if not trigger or trigger == "always_on":
            always_on_bytes += size
            line_count = len(text.splitlines())
            if line_count > ALWAYS_ON_MAX_LINES:
                long_always_on.append(f"{name}:{line_count}")
        for key in NON_PORTABLE_KEYS:
            if key in values:
                non_portable.append(f"{name}:{key}")

    report.add("Rule files within 24 KB", not oversized, ", ".join(oversized))
    report.add("Rule frontmatter valid", not bad_frontmatter,
               f"missing name/description: {', '.join(bad_frontmatter)}" if bad_frontmatter else "")
    report.add("Rule trigger values valid", not bad_trigger, ", ".join(bad_trigger))
    report.add("No non-portable rule keys", not non_portable, ", ".join(non_portable))
    if missing_trigger:
        report.warn("Rule trigger declared",
                    f"no trigger (Antigravity may discard silently): {', '.join(missing_trigger)}")
    if long_always_on:
        report.warn("Always-on rules are short",
                    f"over {ALWAYS_ON_MAX_LINES} lines, move detail to model_decision: "
                    f"{', '.join(long_always_on)}")

    tokens = always_on_bytes // BYTES_PER_TOKEN
    report.add(
        "Always-on rules within 20k tokens",
        tokens <= ALWAYS_ON_TOKEN_FAIL,
        f"~{tokens} tokens from {always_on_bytes} bytes (Antigravity demotes past {ALWAYS_ON_TOKEN_FAIL})",
    )
    if ALWAYS_ON_TOKEN_WARN < tokens <= ALWAYS_ON_TOKEN_FAIL:
        report.warn("Always-on rules token target", f"~{tokens} tokens (target <= {ALWAYS_ON_TOKEN_WARN})")


def check_context(root: str, report: Report) -> None:
    for rel in ("charter.md", "architecture.md"):
        path = os.path.join(root, ".agents", "context", rel)
        exists = os.path.isfile(path)
        report.add(f".agents/context/{rel} exists", exists, "" if exists else "missing")

    charter = os.path.join(root, ".agents", "context", "charter.md")
    if not os.path.isfile(charter):
        return
    text = read_text(charter)
    lower = text.lower()
    # The charter is written in the user's language, so the heading can be
    # Vietnamese. Match either spelling, then judge the bullets under it.
    heading = re.search(r"(?im)^#{1,6}\s*(open questions|cĂ¢u há»i má»Ÿ|cau hoi mo)\s*$", lower)
    if heading is None:
        report.warn("Open questions section", "no 'Open questions' / 'CĂ¢u há»i má»Ÿ' heading found")
        return
    tail = lower[heading.end():]
    next_heading = re.search(r"(?m)^#{1,6}\s", tail)
    section = tail[: next_heading.start()] if next_heading else tail
    bullets = [line.strip() for line in section.splitlines() if line.strip().startswith(("-", "*"))]
    resolved = {"none", "khĂ´ng", "khong", "n/a", "-"}
    open_items = [b for b in bullets if b.lstrip("-* ").strip().strip(".") not in resolved]
    if not open_items:
        report.add("Open questions resolved", True, "")
        return
    # A bullet that names what it blocks is a gate, not a note.
    blocking = [b for b in open_items
                if re.search(r"blocks?\s*[:=]\s*(?!none\b|khĂ´ng\b|khong\b|n/a\b|-)\S", b)]
    report.add("Open questions not blocking", not blocking,
               f"blocks: {', '.join(blocking)[:160]}" if blocking else "")
    if open_items and not blocking:
        report.warn("Open questions present", f"{len(open_items)} non-blocking item(s)")


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(root: str, report: Report) -> dict | None:
    manifest_path = os.path.join(root, ".agents", "skills.manifest.json")
    if not os.path.isfile(manifest_path):
        report.add("skills.manifest.json exists", False, "missing")
        return None
    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        report.add("skills.manifest.json parses", False, str(exc))
        return None
    report.add("skills.manifest.json parses", True, "")
    return manifest if isinstance(manifest, dict) else None


def check_skills(root: str, require_claude: bool, report: Report) -> bool:
    """Returns True when the project selected at least one skill."""
    skills_dir = os.path.join(root, ".agents", "skills")
    manifest = load_manifest(root, report)
    manifest_names = []
    if isinstance(manifest, dict):
        for row in manifest.get("skills") or []:
            if isinstance(row, dict) and isinstance(row.get("name"), str):
                manifest_names.append(row["name"])

    if not os.path.isdir(skills_dir):
        # Selecting no project skills is a legitimate answer (global-only hosts).
        if manifest is not None and not manifest_names:
            report.skip(".agents/skills/", "no project skills selected - allowed")
            report.warn("REGISTRY.md", "absent with zero project skills - expected")
            return False
        report.add(".agents/skills/ exists", False, "missing")
        return bool(manifest_names)

    names = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]
    report.add("Skills installed", True, f"{len(names)} folder(s)")
    budget_detail = "" if len(names) <= DAILY_SKILL_BUDGET else f"{len(names)} > {DAILY_SKILL_BUDGET} - hard cap"
    report.add("Daily skill budget", len(names) <= DAILY_SKILL_BUDGET, budget_detail)

    missing_skill_md, name_mismatch, claude_tokens, extra_keys = [], [], [], []
    for name in names:
        path = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.isfile(path):
            missing_skill_md.append(name)
            continue
        text = read_text(path)
        values, closed = parse_frontmatter(text)
        if not closed:
            extra_keys.append(f"{name}: no frontmatter")
            continue
        declared = normalise_scalar(field_text(values, "name"))
        if declared != name:
            name_mismatch.append(f"{name}->{declared or '(missing)'}")
        extra = {key for key in values if key not in PORTABLE_FRONTMATTER}
        if extra:
            extra_keys.append(f"{name}: {', '.join(sorted(extra))}")
        exec_text = executable_fences(text)
        if any(re.search(pattern, exec_text) for pattern in HOST_SPECIFIC_TOKENS):
            claude_tokens.append(name)

    report.add("Every skill has SKILL.md", not missing_skill_md, ", ".join(missing_skill_md))
    report.add("Skill name matches folder", not name_mismatch, ", ".join(name_mismatch))
    # Installed skills are vendored by definition: report non-portable keys, but
    # never fail on them, because editing a vendored skill is forbidden.
    if extra_keys:
        report.warn("Vendored skill frontmatter", "; ".join(extra_keys))
    else:
        report.add("Vendored skill frontmatter", True, "")
    report.add("No Claude-only substitutions in commands", not claude_tokens,
               f"inside executable fences: {', '.join(claude_tokens)}" if claude_tokens else "")

    if manifest is not None:
        on_disk = set(names)
        listed = set(manifest_names)
        report.add("Manifest matches installed skills", on_disk == listed,
                   f"on disk but not in manifest: {', '.join(sorted(on_disk - listed)) or 'none'}; "
                   f"in manifest but not on disk: {', '.join(sorted(listed - on_disk)) or 'none'}")

    if require_claude:
        claude_dir = os.path.join(root, ".claude", "skills")
        missing, drifted, extra = [], [], []
        for name in names:
            source_dir = os.path.join(skills_dir, name)
            mirror_dir = os.path.join(claude_dir, name)
            if not os.path.isfile(os.path.join(mirror_dir, "SKILL.md")):
                missing.append(name)
                continue
            source_files = set()
            for dirpath, _dirnames, filenames in os.walk(source_dir):
                for filename in filenames:
                    source = os.path.join(dirpath, filename)
                    relative = os.path.relpath(source, source_dir)
                    source_files.add(relative)
                    mirrored = os.path.join(mirror_dir, relative)
                    if not os.path.isfile(mirrored) or sha256(source) != sha256(mirrored):
                        drifted.append(f"{name}/{relative}")
            for dirpath, _dirnames, filenames in os.walk(mirror_dir):
                for filename in filenames:
                    relative = os.path.relpath(os.path.join(dirpath, filename), mirror_dir)
                    if relative not in source_files:
                        extra.append(f"{name}/{relative}")
        report.add("Skills mirrored to .claude/skills/", not missing,
                   f"not mirrored: {', '.join(missing)}" if missing else "")
        report.add("Mirror is byte-identical", not drifted and not extra,
                   f"differs: {', '.join(drifted[:5])}" if drifted
                   else (f"stale on the mirror side: {', '.join(extra[:5])}" if extra else ""))

    report.add("REGISTRY.md exists", os.path.isfile(os.path.join(skills_dir, "REGISTRY.md")),
               "" if os.path.isfile(os.path.join(skills_dir, "REGISTRY.md")) else "missing")
    return True


def read_gitignore(root: str) -> list[str] | None:
    path = os.path.join(root, ".gitignore")
    if not os.path.isfile(path):
        return None
    patterns = []
    for raw in read_text(path).splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _glob_regex(pattern: str) -> str:
    """Translate a gitignore glob into a regex.

    Character by character on purpose: `fnmatch` turns every `*` into `.*`,
    which crosses a `/` where git's `*` stops at it, and `fnmatch` has no
    meaning for `**`. Only these metacharacters exist in a gitignore glob:
    `*` (not across `/`), `?` (one character, not `/`), `[...]`, and the
    `**/` / `/**` / `/**/` forms.
    """
    out: list[str] = []
    index = 0
    length = len(pattern)
    while index < length:
        char = pattern[index]
        if char == "*":
            if pattern.startswith("**", index):
                # `/**/` or a leading `**/`: zero or more path levels.
                after = index + 2
                if pattern.startswith("/", after):
                    out.append("(?:.*/)?")
                    index = after + 1
                    continue
                out.append(".*")
                index = after
                continue
            out.append("[^/]*")
            index += 1
            continue
        if char == "?":
            out.append("[^/]")
            index += 1
            continue
        if char == "[":
            close = pattern.find("]", index + 1)
            if close == -1:
                out.append(re.escape(char))
                index += 1
                continue
            body = pattern[index + 1:close]
            if body.startswith("!"):
                body = "^" + body[1:]
            out.append("[" + body.replace("\\", "\\\\") + "]")
            index = close + 1
            continue
        out.append(re.escape(char))
        index += 1
    return "".join(out)


def _glob_match(pattern: str, target: str) -> bool:
    """Git glob for one path, where `*` never crosses a `/`."""
    try:
        return re.fullmatch(_glob_regex(pattern), target) is not None
    except re.error:
        return fnmatch.fnmatchcase(target, pattern)


def pattern_matches(pattern: str, rel: str, is_dir: bool = False) -> bool:
    """Does THIS pattern match THIS path, as git tests one pattern.

    The answer here is deliberately narrow: only the path itself, never a
    directory above it. Containment is `excluded_ancestor`'s job, and keeping
    the two apart is what makes a negation behave like git's. When this
    function also answered "or the parent matches", a negation such as `!foo/`
    rescued `foo/x.txt` from `*`, and `.agents/**/` wrongly re-included a file
    whose parent it had just excluded.

    - a slash-free pattern is a name and is tested against the basename;
    - any other slash anchors the pattern to the project root, and a leading
      slash only says so out loud;
    - a trailing slash means "a directory": false for a plain file;
    - `**/`, `/**` and `/**/` cross path levels; `*` and `?` never do;
    - `dir/**` covers what is inside `dir`, never `dir` itself.
    """
    dir_only = pattern.endswith("/")
    # Anchoring is a property of the pattern as written: `.agents/**` contains
    # a slash even though the `/**` is removed below, and `/AGENTS.md` is
    # anchored by its leading slash.
    prose = pattern[1:] if pattern.startswith("!") else pattern
    anchored = prose.strip("/") != prose.strip("/").rsplit("/", 1)[-1] \
        or prose.startswith("/")
    body = pattern.rstrip("/")
    trailing_globstar = body.endswith("/**")
    if trailing_globstar:
        body = body[:-3].rstrip("/")
    body = body.strip("/")
    if not body:
        # `/` on its own matches nothing in git.
        return False

    if trailing_globstar:
        # `dir/**` is "everything inside dir", so at least one more segment.
        # The globstar already spans every depth, so `dir/**/` adds only one
        # thing: the pattern is then directory-only - which the caller learns
        # from `is_dir`, not from this string.
        regex = _glob_regex(body) + "/.+"
    else:
        regex = _glob_regex(body)

    if dir_only and not is_dir:
        # git never tries a directory pattern against a plain file, so
        # `.agents/**/` cannot hide `.agents/notes.txt` - only a directory
        # inside `.agents/`, and through it the file.
        return False

    target = rel if anchored else rel.rsplit("/", 1)[-1]
    return re.fullmatch(regex, target) is not None


def excluded_ancestor(rel: str, patterns: list[str]) -> str | None:
    """The nearest ancestor directory that ends up excluded.

    Git decides by last match wins, negations included, and a negation CAN
    rescue an ancestor that an earlier pattern excluded — that is exactly how
    the whitelist idiom (`.agents/*` + `!.agents/skills/`) works. Treating any
    non-negated hit as final reported those files as ignored and failed a
    correct project, so each ancestor is evaluated with the full pass.
    """
    parts = rel.split("/")[:-1]
    for index in range(1, len(parts) + 1):
        ancestor = "/".join(parts[:index])
        state = False
        for pattern in patterns:
            negated = pattern.startswith("!")
            body = pattern[1:] if negated else pattern
            if pattern_matches(body, ancestor, is_dir=True):
                state = not negated
        if state:
            return ancestor
    return None


def ignored_by_patterns(rel: str, patterns: list[str]) -> bool:
    """Git's real rule, applied when git itself cannot be asked.

    One last-match-wins pass over the path and every ancestor directory: the
    nearest match decides, and an excluded parent directory cannot be rescued
    by a later negation, which is why `excluded_ancestor` is asked first.
    """
    if excluded_ancestor(rel, patterns) is not None:
        return True
    return last_match(rel, patterns)


def last_match(rel: str, patterns: list[str]) -> bool:
    """Last matching pattern wins; a negation wins by re-including."""
    state = False
    for pattern in patterns:
        negated = pattern.startswith("!")
        body = pattern[1:] if negated else pattern
        if pattern_matches(body, rel):
            state = not negated
    return state


def git_unavailable_reason(root: str) -> str:
    git = shutil.which("git")
    if git is None:
        return "git not on PATH"
    if not os.path.isdir(os.path.join(root, ".git")):
        return "not a git repository"
    try:
        top = subprocess.run(
            [git, "-C", root, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except OSError as exc:
        return f"git failed: {exc}"
    if top.returncode != 0:
        return "git cannot read the repository (safe.directory or ownership)"
    try:
        if os.path.normcase(os.path.realpath(top.stdout.strip())) != os.path.normcase(os.path.realpath(root)):
            return "project root is not the repository root"
    except OSError:
        return "repository root unknown"
    return "git available"


def git_ignored(root: str, rels: list[str]) -> dict[str, bool] | None:
    """Ask git itself when the project root is the repository root.

    `--no-index` matters: without it check-ignore never reports a *tracked* file,
    so once the charter is committed a later `.agents/` rule would pass silently
    and new rule files would be uncommittable.
    """
    if git_unavailable_reason(root) != "git available":
        return None
    git = shutil.which("git")
    result: dict[str, bool] = {}
    for rel in rels:
        try:
            completed = subprocess.run(
                [git, "-C", root, "check-ignore", "--no-index", "-q", "--", rel],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except OSError:
            return None
        if completed.returncode not in (0, 1):
            return None
        result[rel] = completed.returncode == 0
    return result


def git_ignore_source(root: str, rel: str) -> str:
    """Which ignore file/line matched, for a diagnosis the user can act on."""
    git = shutil.which("git")
    if git is None:
        return ""
    try:
        completed = subprocess.run(
            [git, "-C", root, "check-ignore", "--no-index", "-v", "--", rel],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return ""
    line = completed.stdout.strip()
    return line.split("\t")[0] if line else ""


def check_gitignore(root: str, has_skills: bool, require_claude: bool, report: Report) -> None:
    patterns = read_gitignore(root)
    if patterns is None:
        # With no vendored skills there is nothing to protect the repository
        # from, so a missing .gitignore is advice rather than a gate.
        if has_skills:
            report.add("Check .gitignore", False,
                       "no .gitignore - vendored skills would be committed")
        else:
            report.warn("Check .gitignore", "absent, and no project skills to exclude")
        return

    probes = {
        "vendored skill file": ".agents/skills/__probe__/SKILL.md",
        "REGISTRY.md": ".agents/skills/REGISTRY.md",
        "manifest": ".agents/skills.manifest.json",
        "AGENTS.md": "AGENTS.md",
        "CLAUDE.md": "CLAUDE.md",
        "charter context": ".agents/context/charter.md",
        "rule file": ".agents/rules/__probe__.md",
    }
    if require_claude:
        probes["claude mirror"] = ".claude/skills/__probe__/SKILL.md"

    via_git = git_ignored(root, list(probes.values()))
    if via_git is None:
        reason = git_unavailable_reason(root)
        report.warn("Ignore check", f"approximate, git rules not applied ({reason})")
        ignored = {label: ignored_by_patterns(rel, patterns) for label, rel in probes.items()}
        method = "pattern fallback"
    else:
        ignored = {label: via_git[rel] for label, rel in probes.items()}
        method = "git check-ignore"

    def source(label: str) -> str:
        if method != "git check-ignore":
            return ""
        found = git_ignore_source(root, probes[label])
        return f" (matched by {found})" if found else ""

    if has_skills:
        report.add("Vendored skills ignored", ignored["vendored skill file"],
                   "" if ignored["vendored skill file"]
                   else f"add '.agents/skills/*' to .gitignore ({method})")
        if require_claude:
            report.add(".claude/skills/ ignored", ignored["claude mirror"],
                       "" if ignored["claude mirror"] else "add '.claude/skills/' to .gitignore")
    else:
        report.skip("Vendored skills ignored", "no project skills selected")

    report.add("REGISTRY.md not ignored", not ignored["REGISTRY.md"],
               "" if not ignored["REGISTRY.md"]
               else "a bare '.agents/skills/' also hides the registry: ignore '.agents/skills/*' "
                    f"and re-include '!.agents/skills/REGISTRY.md'{source('REGISTRY.md')}")
    report.add("Manifest not ignored", not ignored["manifest"],
               "" if not ignored["manifest"]
               else f"skills.manifest.json must be committed{source('manifest')}")
    for label in ("AGENTS.md", "CLAUDE.md", "charter context", "rule file"):
        if ignored[label]:
            report.add(f"Charter not ignored ({label})", False,
                       f"the charter must be committed to be shared{source(label)}")


def credential_hits(text: str) -> list[str]:
    hits = []
    for match in CREDENTIAL_RE.finditer(text):
        value = match.group(1)
        if IDENTIFIER_ONLY_RE.match(value):
            continue  # names a variable, which is the recommended style
        hits.append(f"credential assignment ({value[:4]}...)")
    return hits


def placeholder_hits(text: str) -> bool:
    return bool(PLACEHOLDER_RE.search(strip_fences(text)))


def check_secrets_and_paths(root: str, report: Report) -> None:
    hits: list[str] = []
    abs_hits: list[str] = []
    placeholders: list[str] = []
    for path in collect_charter_files(root):
        text = read_text(path)
        rel = os.path.relpath(path, root)
        hits.extend(f"{rel}: {label}" for label in credential_hits(text))
        for pattern, label in SECRET_PATTERNS:
            if re.search(pattern, text):
                hits.append(f"{rel}: {label}")
        for pattern, label in ABS_PATH_PATTERNS:
            if re.search(pattern, text):
                abs_hits.append(f"{rel}: {label}")
        if placeholder_hits(text):
            placeholders.append(rel)
    report.add("No secrets in charter", not hits, "; ".join(sorted(set(hits))))
    report.add("No absolute personal paths", not abs_hits, "; ".join(sorted(set(abs_hits))))
    if placeholders:
        report.warn("No unfilled placeholders",
                    f"still look templated: {', '.join(sorted(placeholders)[:6])}")


def check_referenced_paths(root: str, agents_text: str, report: Report) -> None:
    if not agents_text:
        return
    prefixes = (".agents/", ".claude/", "docs/")
    referenced = set()
    for candidate in CHECK_COMMAND_RE.findall(agents_text):
        token = candidate.strip().rstrip(".,;:")
        if not token or " " in token:
            continue
        # Globs, placeholders, URLs and library-relative paths are not
        # references to files this project must contain.
        if any(marker in token for marker in ("*", "<", ">")):
            continue
        if token.startswith(("env:", "http://", "https://", "_external/", "~")):
            continue
        if token == "SKILL.md":
            continue
        # Optional: a project may legitimately select zero project skills.
        if token.rstrip("/") in OPTIONAL_DIRS:
            continue
        if token in ("AGENTS.md", "CLAUDE.md") or token.startswith(prefixes):
            referenced.add(token)
        elif token.endswith(".md") and "/" in token:
            referenced.add(token)
        # Anything else (`origin/main`, `application/json`) is prose, not a path.
    missing = [rel for rel in sorted(referenced) if not os.path.exists(os.path.join(root, rel))]
    report.add("Paths referenced by AGENTS.md exist", not missing,
               f"missing: {', '.join(missing)}" if missing else f"{len(referenced)} reference(s) checked")


def main(argv: list[str] | None = None) -> int:
    harden_stdout()
    parser = argparse.ArgumentParser(description="Validate a project-charter output.")
    parser.add_argument("project_root", help="Path to the project root to validate")
    parser.add_argument("--claude", action="store_true",
                        help="Require the Claude Code bridge and the .claude/skills mirror")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.project_root)
    if not os.path.isdir(root):
        sys.stderr.write(f"error: not a directory: {root}\n")
        return 2

    report = Report()
    agents_text = check_agents_md(root, report)
    check_claude_bridge(root, args.claude, report)
    check_rules(root, report)
    check_context(root, report)
    has_skills = check_skills(root, args.claude, report)
    check_gitignore(root, has_skills, args.claude, report)
    check_secrets_and_paths(root, report)
    check_referenced_paths(root, agents_text, report)

    if args.json:
        print(json.dumps(
            {
                "root": root,
                "passed": not report.failed,
                "checks": [
                    {"check": c, "status": s, "detail": d} for c, s, d in report.rows
                ],
            },
            indent=2,
            ensure_ascii=False,
        ))
    else:
        failures = sum(1 for _, s, _ in report.rows if s == "FAIL")
        warnings = sum(1 for _, s, _ in report.rows if s == "WARN")
        print(f"Project charter validation - {root}")
        print("-" * 72)
        print(report.render())
        print("-" * 72)
        verdict = "PASS" if not report.failed else f"FAIL ({failures} failing check(s))"
        print(f"RESULT: {verdict} - {warnings} warning(s)")

    return 1 if report.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
