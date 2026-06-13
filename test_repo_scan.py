from app.services.repository_review_service import (
    analyze_repository,
)

result = analyze_repository(
    "https://github.com/pallets/flask"
)

print("FILES:", result["files_scanned"])
print("ISSUES:", result["issues_found"])

for finding in result["findings"][:10]:
    print(finding)