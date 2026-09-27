from datetime import datetime, timezone


def unwrap(data):
    """Unwrap MCP result dictionaries when necessary."""

    if isinstance(data, dict) and "result" in data:
        return data["result"]

    return data


def calculate_contributor_concentration(contributors):
    """Calculate how concentrated recent activity is among contributors."""

    if not contributors:
        return {
            "unique_contributors": 0,
            "top_contributor_share": 0
        }

    total_activity = sum(contributors.values())

    if total_activity == 0:
        return {
            "unique_contributors": len(contributors),
            "top_contributor_share": 0
        }

    top_activity = max(contributors.values())

    top_share = round(
        (top_activity / total_activity) * 100,
        2
    )

    return {
        "unique_contributors": len(contributors),
        "top_contributor_share": top_share
    }


def analyze_repository(repo_data, issues, pull_requests, commits):
    """
    Analyze GitHub repository data and generate
    engineering signals for RepoLens investigation.
    """

    repo_data = unwrap(repo_data)
    issues = unwrap(issues)
    pull_requests = unwrap(pull_requests)
    commits = unwrap(commits)

    # --------------------------------------------------
    # 1. Validate MCP data
    # --------------------------------------------------

    if not isinstance(issues, list):
        issues = []

    if not isinstance(pull_requests, list):
        pull_requests = []

    if not isinstance(commits, list):
        commits = []

    # Remove API errors
    issues = [
        issue
        for issue in issues
        if isinstance(issue, dict)
        and "error" not in issue
    ]

    pull_requests = [
        pr
        for pr in pull_requests
        if isinstance(pr, dict)
        and "error" not in pr
    ]

    commits = [
        commit
        for commit in commits
        if isinstance(commit, dict)
        and "error" not in commit
    ]

    # --------------------------------------------------
    # 2. Basic repository metrics
    # --------------------------------------------------

    total_issues = len(issues)
    total_prs = len(pull_requests)
    total_commits = len(commits)

    # --------------------------------------------------
    # 3. Contributor activity
    # --------------------------------------------------

    contributor_activity = {}

    # Commit contributors
    for commit in commits:

        author = commit.get("author")

        if author:
            contributor_activity[author] = (
                contributor_activity.get(author, 0) + 1
            )

    # PR contributors
    for pr in pull_requests:

        user = pr.get("user")

        if user:
            contributor_activity[user] = (
                contributor_activity.get(user, 0) + 1
            )

    contributor_analysis = calculate_contributor_concentration(
        contributor_activity
    )

    # --------------------------------------------------
    # 4. Stale issue analysis
    # --------------------------------------------------

    stale_issues = []

    now = datetime.now(timezone.utc)

    for issue in issues:

        try:

            updated_at = issue.get("updated_at")

            if not updated_at:
                continue

            updated = datetime.fromisoformat(
                updated_at.replace("Z", "+00:00")
            )

            age_days = (now - updated).days

            if age_days > 30:

                stale_issues.append({
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "age_days": age_days
                })

        except Exception:
            continue

    # --------------------------------------------------
    # 5. Stale issue ratio
    # --------------------------------------------------

    if total_issues > 0:

        stale_issue_ratio = round(
            (len(stale_issues) / total_issues) * 100,
            2
        )

    else:

        stale_issue_ratio = 0

    # --------------------------------------------------
    # 6. Commit activity by date
    # --------------------------------------------------

    commit_activity = {}

    for commit in commits:

        date_value = commit.get("date")

        if date_value:

            date = date_value[:10]

            commit_activity[date] = (
                commit_activity.get(date, 0) + 1
            )

    active_days = len(commit_activity)

    # --------------------------------------------------
    # 7. Development activity signal
    # --------------------------------------------------

    if total_commits == 0:

        development_activity = "Low"

    elif active_days >= 15:

        development_activity = "High"

    elif active_days >= 7:

        development_activity = "Moderate"

    else:

        development_activity = "Concentrated"

    # --------------------------------------------------
    # 8. Issue backlog signal
    # --------------------------------------------------

    if total_issues >= 100:

        issue_backlog = "High"

    elif total_issues >= 30:

        issue_backlog = "Moderate"

    elif total_issues > 0:

        issue_backlog = "Low"

    else:

        issue_backlog = "None detected"

    # --------------------------------------------------
    # 9. Pull request activity signal
    # --------------------------------------------------

    if total_prs >= 50:

        pr_activity = "High"

    elif total_prs >= 15:

        pr_activity = "Moderate"

    elif total_prs > 0:

        pr_activity = "Low"

    else:

        pr_activity = "None detected"

    # --------------------------------------------------
    # 10. Issue / PR relationship
    # --------------------------------------------------

    if total_prs > 0:

        issue_pr_ratio = round(
            total_issues / total_prs,
            2
        )

    else:

        issue_pr_ratio = None

    # --------------------------------------------------
    # 11. Contributor concentration signal
    # --------------------------------------------------

    top_contributor_share = contributor_analysis[
        "top_contributor_share"
    ]

    if top_contributor_share >= 70:

        contributor_concentration = "High"

    elif top_contributor_share >= 40:

        contributor_concentration = "Moderate"

    elif top_contributor_share > 0:

        contributor_concentration = "Distributed"

    else:

        contributor_concentration = "Unknown"

    # --------------------------------------------------
    # 12. Investigation signals
    # --------------------------------------------------

    investigation_signals = []

    if stale_issue_ratio >= 30:

        investigation_signals.append(
            "Large proportion of retrieved issues are stale."
        )

    if issue_pr_ratio is not None and issue_pr_ratio >= 3:

        investigation_signals.append(
            "Issue backlog is substantially larger than the PR backlog."
        )

    if contributor_concentration == "High":

        investigation_signals.append(
            "Recent activity is highly concentrated among a small contributor group."
        )

    if development_activity == "Concentrated":

        investigation_signals.append(
            "Recent commits are concentrated on relatively few days."
        )

    if not investigation_signals:

        investigation_signals.append(
            "No major investigation signal detected from the retrieved sample."
        )

    # --------------------------------------------------
    # 13. Final structured analysis
    # --------------------------------------------------

    return {

        "repository": (
            repo_data.get("name")
            if isinstance(repo_data, dict)
            else "Unknown"
        ),

        "description": (
            repo_data.get("description")
            if isinstance(repo_data, dict)
            else None
        ),

        "stars": (
            repo_data.get("stars")
            if isinstance(repo_data, dict)
            else 0
        ),

        "forks": (
            repo_data.get("forks")
            if isinstance(repo_data, dict)
            else 0
        ),

        "language": (
            repo_data.get("language")
            if isinstance(repo_data, dict)
            else None
        ),

        "metrics": {

            "open_issues_retrieved": total_issues,

            "open_pull_requests_retrieved": total_prs,

            "recent_commits_retrieved": total_commits,

            "active_contributors": contributor_analysis[
                "unique_contributors"
            ],

            "top_contributor_share_percent": top_contributor_share,

            "stale_issues": len(stale_issues),

            "stale_issue_ratio_percent": stale_issue_ratio,

            "active_commit_days": active_days,

            "issue_pr_ratio": issue_pr_ratio
        },

        "signals": {

            "development_activity": development_activity,

            "issue_backlog": issue_backlog,

            "pull_request_activity": pr_activity,

            "contributor_concentration": contributor_concentration,

            "stale_issue_level": (
                "High"
                if stale_issue_ratio >= 30
                else "Moderate"
                if stale_issue_ratio >= 15
                else "Low"
            )
        },

        "investigation_signals": investigation_signals,

        "stale_issue_details": stale_issues[:10],

        "commit_activity": commit_activity,

        "contributor_activity": contributor_activity

    }


if __name__ == "__main__":

    print("RepoLens Analyzer loaded successfully.")