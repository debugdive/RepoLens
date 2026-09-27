import asyncio
import sys
import json

from mcp import Client, StdioServerParameters

from analyzer import analyze_repository
from llm import generate_insight


def extract_tool_result(result):
    """
    Extract the complete value returned by an MCP tool.
    """

    # -----------------------------------------
    # Structured MCP result
    # -----------------------------------------

    if result.structured_content is not None:

        data = result.structured_content

        if isinstance(data, dict) and "result" in data:
            return data["result"]

        return data

    # -----------------------------------------
    # Text MCP result
    # -----------------------------------------

    if result.content:

        # Collect ALL text items.
        text_items = []

        for item in result.content:

            if hasattr(item, "text"):

                text_items.append(item.text)

        if not text_items:
            return None

        # Try each text item as JSON.
        parsed_items = []

        for text in text_items:

            try:
                parsed_items.append(
                    json.loads(text)
                )

            except json.JSONDecodeError:
                parsed_items.append(text)

        # -------------------------------------
        # IMPORTANT:
        # If there are multiple JSON objects,
        # return the complete list.
        # -------------------------------------

        if len(parsed_items) > 1:
            return parsed_items

        return parsed_items[0]

    return None


async def get_repository_data(owner, repo):
    """
    Connect to the MCP server and retrieve
    GitHub repository information.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"]
    )

    async with Client(server_params) as client:

        repo_result = await client.call_tool(
            "get_repository",
            {
                "owner": owner,
                "repo": repo
            }
        )

        issues_result = await client.call_tool(
            "get_issues",
            {
                "owner": owner,
                "repo": repo,
                "state": "open"
            }
        )

        prs_result = await client.call_tool(
            "get_pull_requests",
            {
                "owner": owner,
                "repo": repo,
                "state": "open"
            }
        )

        commits_result = await client.call_tool(
            "get_commits",
            {
                "owner": owner,
                "repo": repo
            }
        )

        repo_data = extract_tool_result(
            repo_result
        )

        issues = extract_tool_result(
            issues_result
        )

        pull_requests = extract_tool_result(
            prs_result
        )

        commits = extract_tool_result(
            commits_result
        )

        return (
            repo_data,
            issues,
            pull_requests,
            commits
        )


async def analyze_with_agent(owner, repo, question):

    print("\n[1/4] Connecting to MCP server...")

    (
        repo_data,
        issues,
        prs,
        commits
    ) = await get_repository_data(
        owner,
        repo
    )

    print("[2/4] GitHub data retrieved through MCP.")

    # -----------------------------------------
    # Safety checks
    # -----------------------------------------

    if not isinstance(issues, list):
        issues = []

    if not isinstance(prs, list):
        prs = []

    if not isinstance(commits, list):
        commits = []

    # -----------------------------------------
    # Analyze GitHub data
    # -----------------------------------------

    analysis = analyze_repository(
        repo_data,
        issues,
        prs,
        commits
    )

    print("[3/4] Repository data analyzed.")

    # -----------------------------------------
    # Generate AI insight
    # -----------------------------------------

    answer = generate_insight(
        analysis,
        question
    )

    print("[4/4] Qwen3 generated the insight.")

    return answer


if __name__ == "__main__":

    answer = asyncio.run(
        analyze_with_agent(
            "microsoft",
            "vscode",
            "Is this repository actively maintained?"
        )
    )

    print("\n")
    print("=" * 50)
    print("             REPOLENS AGENT")
    print("=" * 50)
    print("\n")
    print(answer)
    