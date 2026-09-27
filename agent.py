import asyncio
import json
import sys
import requests

from mcp import Client, StdioServerParameters

from analyzer import analyze_repository
from llm import generate_insight


# ============================================================
# AVAILABLE MCP TOOLS
# ============================================================

AVAILABLE_TOOLS = {
    "repository": (
        "Basic repository information such as "
        "stars, forks, language and last update."
    ),

    "issues": (
        "GitHub issues for analyzing issue backlog "
        "and stale issues."
    ),

    "pull_requests": (
        "Pull requests for analyzing PR activity "
        "and contributor activity."
    ),

    "commits": (
        "Recent commits for analyzing development "
        "activity and contributors."
    )
}


# ============================================================
# EXTRACT DATA FROM MCP RESPONSE
# ============================================================

def extract_tool_result(result):
    """
    Extract the actual data returned by an MCP tool.

    MCP can return structured data or text data.
    This function handles both cases.
    """

    # --------------------------------------------------------
    # Structured response
    # --------------------------------------------------------

    structured = getattr(
        result,
        "structured_content",
        None
    )

    if structured is not None:

        if (
            isinstance(structured, dict)
            and "result" in structured
        ):
            return structured["result"]

        return structured

    # --------------------------------------------------------
    # Text response
    # --------------------------------------------------------

    content = getattr(
        result,
        "content",
        None
    )

    if not content:
        return None

    text_items = []

    for item in content:

        if hasattr(item, "text"):
            text_items.append(item.text)

    if not text_items:
        return None

    parsed_items = []

    for text in text_items:

        try:

            parsed_items.append(
                json.loads(text)
            )

        except json.JSONDecodeError:

            parsed_items.append(text)

    if len(parsed_items) == 1:
        return parsed_items[0]

    return parsed_items


# ============================================================
# FALLBACK TOOL SELECTION
# ============================================================

def fallback_tool_selection(question):
    """
    Select tools using simple rules if Qwen3
    does not return a valid tool plan.

    This makes the application more reliable.
    """

    question_lower = question.lower()

    selected = set()

    # --------------------------------------------------------
    # Repository information
    # --------------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "repository",
            "repo",
            "stars",
            "forks",
            "language",
            "updated",
            "overview"
        ]
    ):
        selected.add("repository")

    # --------------------------------------------------------
    # Issues
    # --------------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "issue",
            "issues",
            "backlog",
            "stale",
            "bug",
            "bugs"
        ]
    ):
        selected.add("issues")

    # --------------------------------------------------------
    # Pull requests
    # --------------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "pull request",
            "pull requests",
            "pr",
            "prs",
            "merge"
        ]
    ):
        selected.add("pull_requests")

    # --------------------------------------------------------
    # Commits
    # --------------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "commit",
            "commits",
            "development",
            "activity",
            "recent"
        ]
    ):
        selected.add("commits")

    # --------------------------------------------------------
    # Broad investigation questions
    # --------------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "investigate",
            "concern",
            "concerns",
            "health",
            "maintained",
            "maintenance",
            "problem",
            "problems",
            "risk",
            "risks"
        ]
    ):
        selected.update(
            {
                "repository",
                "issues",
                "pull_requests",
                "commits"
            }
        )

    # --------------------------------------------------------
    # Safe default
    # --------------------------------------------------------

    if not selected:

        selected.update(
            {
                "repository",
                "issues",
                "pull_requests",
                "commits"
            }
        )

    return list(selected)


# ============================================================
# QWEN3 TOOL PLANNER
# ============================================================

def select_tools(question):
    """
    Ask Qwen3 which MCP tools are necessary
    for the user's question.
    """

    tool_descriptions = json.dumps(
        AVAILABLE_TOOLS,
        indent=2
    )

    prompt = f"""
You are the planning component of RepoLens.

User question:
{question}

Available MCP tools:
{tool_descriptions}

Choose only the tools necessary to answer the question.

Return ONLY the exact tool names,
separated by commas.

Possible names:

repository
issues
pull_requests
commits

Do not explain your answer.
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",

            json={
                "model": "qwen3:1.7b",
                "prompt": prompt,
                "stream": False,

                # Prevent Qwen3 from spending time
                # generating a separate thinking process.
                "think": False,

                "options": {
                    "temperature": 0,
                    "num_predict": 30
                }
            },

            timeout=60
        )

        if response.status_code != 200:
            return fallback_tool_selection(question)

        raw_answer = response.json().get(
            "response",
            ""
        ).strip().lower()

        selected = []

        for tool_name in AVAILABLE_TOOLS:

            if tool_name in raw_answer:
                selected.append(tool_name)

        # If Qwen3 gave a usable answer, use it.
        if selected:
            return selected

        # Otherwise use the fallback rules.
        return fallback_tool_selection(question)

    except Exception:

        return fallback_tool_selection(question)


# ============================================================
# CALL MCP TOOLS
# ============================================================

async def get_repository_data(
    owner,
    repo,
    selected_tools
):
    """
    Connect to the MCP server and call only
    the tools selected by the agent.
    """

    # Default empty values
    repo_data = {}
    issues = []
    pull_requests = []
    commits = []

    # --------------------------------------------------------
    # MCP server configuration
    # --------------------------------------------------------

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"]
    )

    # --------------------------------------------------------
    # Connect to MCP
    # --------------------------------------------------------

    async with Client(server_params) as client:

        # ----------------------------------------------------
        # Repository tool
        # ----------------------------------------------------

        if "repository" in selected_tools:

            result = await client.call_tool(
                "get_repository",
                {
                    "owner": owner,
                    "repo": repo
                }
            )

            repo_data = extract_tool_result(
                result
            )

        # ----------------------------------------------------
        # Issues tool
        # ----------------------------------------------------

        if "issues" in selected_tools:

            result = await client.call_tool(
                "get_issues",
                {
                    "owner": owner,
                    "repo": repo,
                    "state": "open"
                }
            )

            issues = extract_tool_result(
                result
            )

        # ----------------------------------------------------
        # Pull request tool
        # ----------------------------------------------------

        if "pull_requests" in selected_tools:

            result = await client.call_tool(
                "get_pull_requests",
                {
                    "owner": owner,
                    "repo": repo,
                    "state": "open"
                }
            )

            pull_requests = extract_tool_result(
                result
            )

        # ----------------------------------------------------
        # Commits tool
        # ----------------------------------------------------

        if "commits" in selected_tools:

            result = await client.call_tool(
                "get_commits",
                {
                    "owner": owner,
                    "repo": repo
                }
            )

            commits = extract_tool_result(
                result
            )

    return (
        repo_data,
        issues,
        pull_requests,
        commits
    )


# ============================================================
# MAIN AGENT WORKFLOW
# ============================================================

async def analyze_with_agent(
    owner,
    repo,
    question
):
    """
    Run the complete RepoLens workflow.

    Step 1:
    Decide which tools are needed.

    Step 2:
    Retrieve evidence through MCP.

    Step 3:
    Analyze the evidence.

    Step 4:
    Ask Qwen3 to investigate the evidence.
    """

    # --------------------------------------------------------
    # STEP 1 — Planning
    # --------------------------------------------------------

    selected_tools = select_tools(
        question
    )

    # --------------------------------------------------------
    # STEP 2 — MCP data retrieval
    # --------------------------------------------------------

    (
        repo_data,
        issues,
        pull_requests,
        commits
    ) = await get_repository_data(
        owner,
        repo,
        selected_tools
    )

    # --------------------------------------------------------
    # STEP 3 — Python analysis
    # --------------------------------------------------------

    analysis = analyze_repository(
        repo_data,
        issues,
        pull_requests,
        commits
    )

    # --------------------------------------------------------
    # STEP 4 — AI investigation
    # --------------------------------------------------------

    answer = generate_insight(
        analysis,
        question
    )

    return {
        "selected_tools": selected_tools,
        "analysis": analysis,
        "answer": answer
    }


# ============================================================
# TEST THE AGENT DIRECTLY
# ============================================================

if __name__ == "__main__":

    result = asyncio.run(
        analyze_with_agent(
            "microsoft",
            "vscode",
            "Investigate potential engineering concerns."
        )
    )

    print("\nSelected MCP tools:")

    for tool in result["selected_tools"]:
        print(
            f"- {tool}"
        )

    print("\n")

    print(
        result["answer"]
    )