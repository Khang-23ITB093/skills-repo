#!/usr/bin/env python3
"""
compact_log.py <input> [-o output] [--max-lines 200]
Chuẩn hoá (uuid/timestamp/số/hex) và gộp dòng lặp thành "(xN)" để tiết kiệm token.
Khi vượt --max-lines: ưu tiên giữ dòng có error/exception/fatal/traceback/panic/fail/timeout.
"""
import argparse, re, sys

NORM = [
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I), "<uuid>"),
    (re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?"), "<ts>"),
    (re.compile(r"\b0x[0-9a-fA-F]+\b"), "<hex>"),
    (re.compile(r"\b(?:\d{1,2}|\d{4,})\b"), "<n>"),   # giữ nguyên số 3 chữ số (HTTP 404/500, port 443)
]
KEY = re.compile(r"(?i)error|exception|fatal|traceback|panic|fail|timeout")

AGGRESSIVE = NORM[:3] + [(re.compile(r"\b\d+\b"), "<n>")]   # tầng 2: gộp mọi số

def norm(line, rules=NORM):
    for rx, rep in rules: line = rx.sub(rep, line)
    return line

def group(raw_lines, rules):
    groups, order = {}, []
    for raw in raw_lines:
        sig = norm(raw, rules)
        if sig in groups: groups[sig][0] += 1
        else: groups[sig] = [1, raw]; order.append(sig)
    return [(groups[s][1], groups[s][0]) for s in order]

def main():
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("-o"); ap.add_argument("--max-lines", type=int, default=200)
    a = ap.parse_args()
    with open(a.inp, encoding="utf-8", errors="replace") as f:
        raw_lines = [r.rstrip("\r\n") for r in f if r.strip()]
    if len(raw_lines) <= a.max_lines:
        text = "\n".join(raw_lines) + "\n"
        if a.o:
            with open(a.o, "w", encoding="utf-8") as f: f.write(text)
            print(f"{a.inp}: {len(raw_lines)} dòng (dưới trần max-lines, giữ nguyên)", file=sys.stderr)
        else:
            sys.stdout.write(text)
        return

    items = group(raw_lines, NORM)
    if len(items) > a.max_lines:          # vẫn quá dài -> gộp mạnh tay hơn
        items = group(raw_lines, AGGRESSIVE)
    unique_count = len(items)
    lines = [f"{raw}  (x{n})" if n > 1 else raw for raw, n in items]
    dropped = 0
    if len(lines) > a.max_lines:
        keep = [i for i, l in enumerate(lines) if KEY.search(l)][: a.max_lines]
        keep_set = set(keep)
        for i in range(len(lines)):
            if len(keep_set) >= a.max_lines: break
            keep_set.add(i)
        dropped = len(lines) - len(keep_set)
        lines = [lines[i] for i in sorted(keep_set)]
        lines.append(f"... [{dropped} dòng duy nhất khác đã bị lược]")
    text = "\n".join(lines) + "\n"
    if a.o:
        with open(a.o, "w", encoding="utf-8") as f: f.write(text)
        print(f"{a.inp}: {unique_count} cụm duy nhất -> {len(lines)} dòng; {len(text)} ký tự", file=sys.stderr)
    else:
        sys.stdout.write(text)

if __name__ == "__main__":
    main()
