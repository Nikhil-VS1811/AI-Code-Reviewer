from app.services.github_service import (
    clone_repository,
    cleanup_repository,
)
from app.services.repository_scanner import (
    collect_source_files,
)
from app.services.security.static_scanner import (
    scan_code,
)


def _clamp_health_score(score: int) -> int:
    return max(0, min(100, score))


def _build_repository_summary(
    files_scanned: int,
    critical: int,
    high: int,
    medium: int,
    low: int,
    findings: list[dict],
) -> dict:
    health_score = _clamp_health_score(
        100
        - (critical * 10)
        - (high * 5)
        - (medium * 2)
        - low
    )

    strengths = []
    if files_scanned > 0:
        strengths.append("Source files were discovered and analyzed successfully")
    if critical == 0:
        strengths.append("No critical security findings detected")
    if high == 0:
        strengths.append("No high severity findings detected")
    if files_scanned >= 10:
        strengths.append("Repository contains a structured source layout")
    if not findings:
        strengths.append("Static security scan completed without findings")

    weaknesses = []
    if critical:
        weaknesses.append("Critical security findings detected")
    if high:
        weaknesses.append("High severity security findings detected")
    if medium:
        weaknesses.append("Medium severity findings should be reviewed")
    if low:
        weaknesses.append("Low severity cleanup opportunities detected")
    if any("eval" in finding["comment"].lower() for finding in findings):
        weaknesses.append("Unsafe code execution patterns found")
    if any("exec" in finding["comment"].lower() for finding in findings):
        weaknesses.append("Dynamic execution usage increases security risk")
    if any("xss" in finding["comment"].lower() for finding in findings):
        weaknesses.append("Potential cross-site scripting risks detected")
    if not weaknesses:
        weaknesses.append("No major weaknesses detected by the static scanner")

    recommendations = []
    comments = " ".join(finding["comment"].lower() for finding in findings)
    if "eval" in comments:
        recommendations.append("Replace eval() usage with safer parsing or explicit control flow")
    if "exec" in comments:
        recommendations.append("Remove exec() where possible")
    if "shell=true" in comments or "command execution" in comments:
        recommendations.append("Avoid shell command execution and validate command inputs")
    if "pickle.loads" in comments:
        recommendations.append("Avoid unsafe deserialization with pickle.loads()")
    if "innerhtml" in comments or "xss" in comments:
        recommendations.append("Use safe DOM APIs instead of innerHTML")
    if findings:
        recommendations.append("Add input validation around security-sensitive code paths")
        recommendations.append("Prioritize fixes by severity before merging new changes")
    else:
        recommendations.append("Continue running repository scans before releases")
        recommendations.append("Keep dependency and security review practices current")

    return {
        "repository_health_score": health_score,
        "strengths": strengths[:5],
        "weaknesses": weaknesses[:5],
        "recommendations": recommendations[:5],
    }


def analyze_repository(repo_url: str):
    repo_path = clone_repository(repo_url)

    try:
        files = collect_source_files(repo_path)

        findings = []

        for file in files:
            try:
                content = file.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

                file_findings = scan_code(content)

                for finding in file_findings:
                    findings.append(
                        {
                            "file": file.relative_to(repo_path).as_posix(),
                            **finding,
                        }
                    )

            except Exception:
                continue

        critical = sum(
            1
            for finding in findings
            if finding["severity"] == "critical"
        )

        high = sum(
            1
            for finding in findings
            if finding["severity"] == "high"
        )

        medium = sum(
            1
            for finding in findings
            if finding["severity"] == "medium"
        )

        low = sum(
            1
            for finding in findings
            if finding["severity"] == "low"
        )

        summary = _build_repository_summary(
            files_scanned=len(files),
            critical=critical,
            high=high,
            medium=medium,
            low=low,
            findings=findings,
        )

        return {
            "files_scanned": len(files),
            "issues_found": len(findings),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "findings": findings,
            **summary,
        }

    finally:
        cleanup_repository(repo_path)
