import re


SECURITY_RULES = [

    # ---------- Python ----------
    {
        "pattern": r"eval\s*\(",
        "severity": "critical",
        "category": "security",
        "message": "Use of eval() detected.",
    },
    {
        "pattern": r"exec\s*\(",
        "severity": "critical",
        "category": "security",
        "message": "Use of exec() detected.",
    },
    {
        "pattern": r"pickle\.loads\s*\(",
        "severity": "high",
        "category": "security",
        "message": "pickle.loads() may execute arbitrary code.",
    },
    {
        "pattern": r"os\.system\s*\(",
        "severity": "high",
        "category": "security",
        "message": "os.system() command execution detected.",
    },
    {
        "pattern": r"shell\s*=\s*True",
        "severity": "critical",
        "category": "security",
        "message": "subprocess shell=True detected.",
    },

    # ---------- JavaScript / TypeScript ----------
    {
        "pattern": r"innerHTML",
        "severity": "high",
        "category": "security",
        "message": "innerHTML may cause XSS vulnerabilities.",
    },
    {
        "pattern": r"new\s+Function\s*\(",
        "severity": "critical",
        "category": "security",
        "message": "new Function() detected.",
    },
    {
        "pattern": r"document\.write\s*\(",
        "severity": "high",
        "category": "security",
        "message": "document.write() detected.",
    },

    # ---------- Java ----------
    {
        "pattern": r"Runtime\.getRuntime\s*\(\)\.exec\s*\(",
        "severity": "critical",
        "category": "security",
        "message": "Runtime.exec() detected.",
    },
    {
        "pattern": r"ProcessBuilder\s*\(",
        "severity": "high",
        "category": "security",
        "message": "ProcessBuilder execution detected.",
    },

    # ---------- C / C++ ----------
    {
        "pattern": r"system\s*\(",
        "severity": "critical",
        "category": "security",
        "message": "system() call detected.",
    },
    {
        "pattern": r"popen\s*\(",
        "severity": "high",
        "category": "security",
        "message": "popen() detected.",
    },
    {
        "pattern": r"gets\s*\(",
        "severity": "critical",
        "category": "security",
        "message": "Unsafe gets() usage detected.",
    },
    {
        "pattern": r"strcpy\s*\(",
        "severity": "high",
        "category": "security",
        "message": "strcpy() may cause buffer overflows.",
    },
]

def scan_code(code: str):
    findings = []

    lines = code.splitlines()

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