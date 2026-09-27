import asyncio

from agent import analyze_with_agent


def get_repository():
    """Get GitHub repository from the user."""

    while True:
        repository = input(
            "\nGitHub repository (owner/repository): "
        ).strip()

        parts = repository.strip("/ ").split("/")

        if len(parts) == 2 and parts[0] and parts[1]:
            return parts[0], parts[1]

        print(
            "\nInvalid format."
            "\nExample: microsoft/vscode"
        )


def main():
    print("\n" + "=" * 60)
    print("                         REPOLENS")
    print("       Autonomous Software Repository Investigator")
    print("=" * 60)

    print(
        "\nRepoLens uses:"
        "\n• MCP for GitHub tool communication"
        "\n• GitHub API for repository evidence"
        "\n• Python for data analysis"
        "\n• Qwen3 for planning and investigation"
    )

    owner, repo = get_repository()

    question = input(
        "\nWhat should RepoLens investigate?\n> "
    ).strip()

    if not question:
        question = (
            "Identify potential engineering concerns "
            "in this repository."
        )

    print(
        "\n[1/5] Agent is selecting required MCP tools..."
    )

    try:
        result = asyncio.run(
            analyze_with_agent(
                owner,
                repo,
                question
            )
        )

        selected_tools = result["selected_tools"]
        answer = result["answer"]

        print(
            "\n[2/5] MCP tools selected:"
        )

        for tool in selected_tools:
            print(f"      -> {tool}")

        print(
            "\n[3/5] GitHub evidence retrieved through MCP."
        )

        print(
            "[4/5] Repository evidence analyzed."
        )

        print(
            "[5/5] Qwen3 generated the investigation."
        )

        print("\n" + "=" * 60)
        print("                    REPOLENS RESULT")
        print("=" * 60)

        print("\n" + answer)

        print("\n" + "=" * 60)

    except Exception as error:
        print("\nRepoLens encountered an error:")
        print(error)


if __name__ == "__main__":
    main()