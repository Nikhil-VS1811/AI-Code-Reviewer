export interface GuestFinding {
  id: number;
  line_number: number;
  severity: "critical" | "high" | "medium" | "low";
  category: "security" | "performance" | "maintainability" | "readability";
  comment: string;
  remediation: string;
}

export interface GuestReviewData {
  language: string;
  overall_score: number;
  security_score: number;
  performance_score: number;
  maintainability_score: number;
  readability_score: number;
  summary: string;
  code: string;
  findings: GuestFinding[];
}

export const GUEST_SAMPLE_REVIEW: GuestReviewData = {
  language: "python",
  overall_score: 68,
  security_score: 45,
  performance_score: 70,
  maintainability_score: 75,
  readability_score: 82,
  summary:
    "The submission provides core authentication and telemetry helpers, but contains critical security risks including dynamic expression evaluation via eval(), unsanitized subprocess invocation with shell=True, redundant O(N^2) token iterations, and broad unhandled exceptions. Remediate the dynamic evaluation vulnerability before deploying to production.",
  code: `import os
import subprocess
from datetime import datetime, timezone

class SessionValidator:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
        self.active_sessions: dict[str, dict] = {}

    def verify_expression(self, expr_string: str) -> bool:
        # Evaluate user-supplied conditional permission rule
        # WARNING: Untrusted string evaluation
        return bool(eval(expr_string))

    def capture_git_revision(self) -> str:
        # Check system git status for telemetry
        # WARNING: shell=True exposes command injection risk
        cmd = "git rev-parse --short HEAD"
        result = subprocess.check_output(cmd, shell=True)
        return result.decode("utf-8").strip()

    def validate_access(self, user_role: str, scopes: list[str]) -> bool:
        # Verify access scopes against permitted roles
        # Note: redundant linear scan over allowed_roles list
        for scope in scopes:
            for role in self.allowed_roles:
                if role == user_role and scope.startswith("read:"):
                    return True
        return False

    def handle_auth_request(self, payload: dict) -> dict:
        try:
            token = payload["token"]
            return {"authenticated": True, "token": token}
        except Exception:
            # Broad exception catch without logging or error classification
            return {"authenticated": False, "error": "unknown"}
`,
  findings: [
    {
      id: 1,
      line_number: 14,
      severity: "critical",
      category: "security",
      comment:
        "Dangerous dynamic evaluation via eval() detected. Passing user-supplied expressions to eval() allows arbitrary code execution on the server.",
      remediation:
        "Remove eval() entirely. Use a safe parsing grammar (e.g., ast.literal_eval) or deterministic boolean predicate functions.",
    },
    {
      id: 2,
      line_number: 22,
      severity: "high",
      category: "security",
      comment:
        "Subprocess execution with shell=True detected. If command arguments contain untrusted inputs, it enables arbitrary shell command injection.",
      remediation:
        "Execute subprocess commands as an argument vector (e.g., ['git', 'rev-parse', '--short', 'HEAD']) without shell=True.",
    },
    {
      id: 3,
      line_number: 31,
      severity: "medium",
      category: "performance",
      comment:
        "Nested loop linear scan over allowed_roles creates O(N * M) algorithmic complexity on large scope lists.",
      remediation:
        "Convert self.allowed_roles to a set (set(self.allowed_roles)) for O(1) constant-time membership lookups.",
    },
    {
      id: 4,
      line_number: 39,
      severity: "low",
      category: "maintainability",
      comment:
        "Broad except Exception clause silently catches all errors without logging, error classification, or traceback preservation.",
      remediation:
        "Catch specific exceptions (e.g., KeyError, ValueError) and record structured error logs using logging.exception().",
    },
  ],
};
