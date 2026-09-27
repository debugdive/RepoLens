from llm import generate_insight


analysis = {
    "repository": "microsoft/vscode",

    "metrics": {
        "open_issues": 30,
        "open_pull_requests": 30,
        "recent_commits": 30,
        "active_contributors": 31,
        "stale_issues": 0
    },

    "commit_activity": {
        "2026-09-26": 11,
        "2026-09-25": 19
    }
}


question = "Is this repository actively maintained?"

answer = generate_insight(
    analysis,
    question
)

print("\n========== REPOLENS AI ==========\n")
print(answer)
