import re


SECURITY_RULES = [

    # ---------- Python ----------
    {
        "pattern": r"\beval\s*\(",
        "severity": "critical",
        "category": "security",
        "message": "Use of eval() detected.",
    },
    {
        "pattern": r"\bexec\s*\(",
        "severity": "critical",
        "category": "security",
        "message": "Use of exec() detected.",
    },
    {
        "pattern": r"\bpickle\.loads\s*\(",
        "severity": "high",
        "category": "security",
        "message": "pickle.loads() may execute arbitrary code.",
    },
    {
        "pattern": r"\bos\.system\s*\(",
        "severity": "high",
        "category": "security",
        "message": "os.system() command execution detected.",
    },
    {
        "pattern": r"\bshell\s*=\s*True",
        "severity": "critical",
        "category": "security",
        "message": "subprocess shell=True detected.",
    },

    # ---------- JavaScript / TypeScript ----------
    {
        "pattern": r"\binnerHTML\b",
        "severity": "high",
        "category": "security",
        "message": "innerHTML may cause XSS vulnerabilities.",
    },
    {
        "pattern": r"\bnew\s+Function\s*\(",
        "severity": "critical",
        "category": "security",
        "message": "new Function() detected.",
    },
    {
        "pattern": r"\bdocument\.write\s*\(",
        "severity": "high",
        "category": "security",
        "message": "document.write() detected.",
    },

    # ---------- Java ----------
    {
        "pattern": r"\bRuntime\.getRuntime\s*\(\)\.exec\s*\(",
        "severity": "critical",
        "category": "security",
        "message": "Runtime.exec() detected.",
    },
    {
        "pattern": r"\bProcessBuilder\s*\(",
        "severity": "high",
        "category": "security",
        "message": "ProcessBuilder execution detected.",
    },

    # ---------- C / C++ ----------
    {
        "pattern": r"(?<![\.\w])system\s*\(",
        "severity": "critical",
        "category": "security",
        "message": "system() call detected.",
    },
    {
        "pattern": r"(?<![\.\w])popen\s*\(",
        "severity": "high",
        "category": "security",
        "message": "popen() detected.",
    },
    {
        "pattern": r"\bgets\s*\(",
        "severity": "critical",
        "category": "security",
        "message": "Unsafe gets() usage detected.",
    },
    {
        "pattern": r"\bstrcpy\s*\(",
        "severity": "high",
        "category": "security",
        "message": "strcpy() may cause buffer overflows.",
    },
]


def mask_inert_code(code: str) -> list[str]:
    """Mask block comments, docstrings, and line comments with whitespace.

    Preserves line count and original line numbering while preventing benign
    comments or docstrings from triggering false-positive security findings.
    """
    def blank_non_newlines(match: re.Match) -> str:
        text = match.group(0)
        return "".join("\n" if c == "\n" else " " for c in text)

    # 1. Mask C/C++/JS block comments /* ... */
    masked = re.sub(r"/\*[\s\S]*?\*/", blank_non_newlines, code)
    # 2. Mask Python triple-quoted docstrings / multiline strings
    masked = re.sub(r'"""[\s\S]*?"""', blank_non_newlines, masked)
    masked = re.sub(r"'''[\s\S]*?'''", blank_non_newlines, masked)

    lines = masked.splitlines()
    clean_lines: list[str] = []

    for line in lines:
        in_quote: str | None = None
        cleaned_chars: list[str] = []
        i = 0
        n = len(line)
        while i < n:
            ch = line[i]
            if in_quote:
                if ch == "\\":
                    cleaned_chars.append(ch)
                    if i + 1 < n:
                        cleaned_chars.append(line[i + 1])
                        i += 2
                        continue
                elif ch == in_quote:
                    in_quote = None
                cleaned_chars.append(ch)
                i += 1
            else:
                if ch in ('"', "'"):
                    in_quote = ch
                    cleaned_chars.append(ch)
                    i += 1
                elif ch == "#" or (ch == "/" and i + 1 < n and line[i + 1] == "/"):
                    # Rest of line is comment; break to discard
                    break
                else:
                    cleaned_chars.append(ch)
                    i += 1

        clean_lines.append("".join(cleaned_chars))

    return clean_lines


def scan_code(code: str) -> list[dict]:
    if not code:
        return []

    findings: list[dict] = []
    lines = mask_inert_code(code)

    for line_number, line in enumerate(lines, start=1):
        for rule in SECURITY_RULES:
            if re.search(rule["pattern"], line):
                findings.append(
                    {
                        "line_number": line_number,
                        "severity": rule["severity"],
                        "category": rule["category"],
                        "comment": rule["message"],
                    }
                )

    return findings
