import requests
from mcp.server import MCPServer

mcp = MCPServer("RepoLens")

BASE_URL = "https://api.github.com"


@mcp.tool()
def get_repository(owner: str, repo: str) -> dict:
    """Get basic information about a GitHub repository."""

    response = requests.get(
        f"{BASE_URL}/repos/{owner}/{repo}"
    )

    if response.status_code != 200:
        return {"error": f"GitHub API returned {response.status_code}"}

    data = response.json()

    return {
        "name": data["full_name"],
        "description": data["description"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "language": data["language"],
        "updated_at": data["updated_at"]
    }


@mcp.tool()
def get_issues(owner: str, repo: str, state: str = "open") -> list:
    """Get issues from a GitHub repository."""

    response = requests.get(
        f"{BASE_URL}/repos/{owner}/{repo}/issues",
        params={
            "state": state,
            "per_page": 30
        }
    )

    if response.status_code != 200:
        return [{"error": f"GitHub API returned {response.status_code}"}]

    issues = []

    for item in response.json():

        # GitHub's issues endpoint also returns pull requests.
        if "pull_request" in item:
            continue

        issues.append({
            "number": item["number"],
            "title": item["title"],
            "state": item["state"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
            "comments": item["comments"]
        })

    return issues


@mcp.tool()
def get_pull_requests(
    owner: str,
    repo: str,
    state: str = "open"
) -> list:
    """Get pull requests from a GitHub repository."""

    response = requests.get(
        f"{BASE_URL}/repos/{owner}/{repo}/pulls",
        params={
            "state": state,
            "per_page": 30
        }
    )

    if response.status_code != 200:
        return [{"error": f"GitHub API returned {response.status_code}"}]

    pull_requests = []

    for pr in response.json():

        pull_requests.append({
            "number": pr["number"],
            "title": pr["title"],
            "state": pr["state"],
            "created_at": pr["created_at"],
            "updated_at": pr["updated_at"],
            "user": pr["user"]["login"]
        })

    return pull_requests


@mcp.tool()
def get_commits(owner: str, repo: str) -> list:
    """Get recent commits from a GitHub repository."""

    response = requests.get(
        f"{BASE_URL}/repos/{owner}/{repo}/commits",
        params={
            "per_page": 30
        }
    )

    if response.status_code != 200:
        return [{"error": f"GitHub API returned {response.status_code}"}]

    commits = []

    for commit in response.json():

        commits.append({
            "sha": commit["sha"][:7],
            "message": commit["commit"]["message"].split("\n")[0],
            "author": commit["commit"]["author"]["name"],
            "date": commit["commit"]["author"]["date"]
        })

    return commits


if __name__ == "__main__":
    mcp.run()