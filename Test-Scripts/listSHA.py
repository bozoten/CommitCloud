from github import Github

# Authenticate using a personal access token
g = Github("")

# Access the repository (replace with your repository details)
repo = g.get_repo("bozoten/repo2")

# Define the initial and new SHAs
old_sha = ""
new_sha = ""

# Compare the two commits
comparison = repo.compare(old_sha, new_sha)

# List all commits between the two SHAs
for commit in comparison.commits:
    print(f"Commit SHA: {commit.sha}, Message: {commit.commit.message}")
