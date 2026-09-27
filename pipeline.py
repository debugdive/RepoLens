import requests
from analyzer import analyze_repository


BASE_URL = "https://api.github.com"


def get_github_data(owner, repo):

    repo_response = requests.get(
        f"{BASE_URL}/repos/{owner}/{repo}"
    )

    issues_response = requests.get(
        f"{BASE_URL}/repos/{owner}/{repo}/issues",
        params={"state": "open", "per_page": 30}
    )

    prs_response = requests.get(
        f"{BASE_URL}/repos/{owner}/{repo}/pulls",
        params={"state": "open", "per_page": 30}
    )

    commits_response = requests.get(
        f"{BASE_URL}/repos/{owner}/{repo}/commits",
        params={"per_page": 30}
    )

    repo_data = repo_response.json()

    issues = [
        {
            "number": x["number"],
            "title": x["title"],
            "state": x["state"],
            "created_at": x["created_at"],
            "updated_at": x["updated_at"],
            "comments": x["comments"]
        }
        for x in issues_response.json()
        if "pull_request" not in x
    ]

    pull_requests = [
        {
            "number": x["number"],
            "title": x["title"],
            "state": x["state"],
            "created_at": x["created_at"],
            "updated_at": x["updated_at"],
            "user": x["user"]["login"]
        }
        for x in prs_response.json()
    ]

    commits = [
        {
            "sha": x["sha"][:7],
            "message": x["commit"]["message"].split("\n")[0],
            "author": x["commit"]["author"]["name"],
            "date": x["commit"]["author"]["date"]
        }
        for x in commits_response.json()
    ]

    repo_info = {
        "name": repo_data["full_name"],
        "description": repo_data["description"],
        "stars": repo_data["stargazers_count"],
        "forks": repo_data["forks_count"],
        "language": repo_data["language"]
    }

    return repo_info, issues, pull_requests, commits


if __name__ == "__main__":

    owner = "microsoft"
    repo = "vscode"

    repo_data, issues, prs, commits = get_github_data(
        owner,
        repo
    )

    analysis = analyze_repository(
        repo_data,
        issues,
        prs,
        commits
    )

    print("\n========== REPO LENS ANALYSIS ==========\n")

    print("Repository:", analysis["repository"])

    print("\nMetrics:")

    for key, value in analysis["metrics"].items():
        print(f"{key}: {value}")

    print("\nStale Issues:")

    for issue in analysis["stale_issue_details"]:
        print(
            f"#{issue['number']} - "
            f"{issue['title']} "
            f"({issue['age_days']} days)"
        )

    print("\nCommit Activity:")

    for date, count in analysis["commit_activity"].items():
        print(f"{date}: {count}")
        