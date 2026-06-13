from app.services.github_service import clone_repository
from app.services.repository_scanner import collect_source_files

repo = clone_repository(
    "https://github.com/pallets/flask"
)

files = collect_source_files(repo)

print(f"FILES FOUND: {len(files)}")

for file in files[:20]:
    print(file)