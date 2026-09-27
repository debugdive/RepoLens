import asyncio

from agent import analyze_with_agent


def print_header():
    """Display RepoLens header."""

    print("\n" + "=" * 60)
    print("                         🔎 REPOLENS")
    print("              GenAI GitHub Project Analyst")
    print("=" * 60)


def get_repository():
    """Ask the user for a GitHub repository."""

    while True:

        repository = input(
            "\nGitHub repository (owner/repository): "
        ).strip()

        # Remove accidental spaces or trailing /
        repository = repository.strip("/ ")

        if "/" not in repository:

            print(
                "\n❌ Invalid format."
                "\nUse: owner/repository"
                "\nExample: microsoft/vscode"
            )

            continue

        parts = repository.split("/")

        if len(parts) != 2:

            print(
                "\n❌ Invalid repository format."
                "\nExample: microsoft/vscode"
            )

            continue

        owner = parts[0].strip()
        repo = parts[1].strip()

        if not owner or not repo:

            print(
                "\n❌ Owner and repository name cannot be empty."
            )

            continue

        return owner, repo


def get_question():
    """Ask the user what they want to know."""

    while True:

        question = input(
            "\nYour question: "
        ).strip()

        if question:

            return question

        print("\n❌ Please enter a question.")


def run_analysis(owner, repo, question):
    """Run the RepoLens AI analysis."""

    print("\n" + "-" * 60)

    print("\n[1/4] Connecting to MCP server...")

    try:

        answer = asyncio.run(
            analyze_with_agent(
                owner,
                repo,
                question
            )
        )

        print("\n[2/4] GitHub data retrieved through MCP.")
        print("[3/4] Repository data analyzed.")
        print("[4/4] Qwen3 generated the insight.")

        print("\n" + "=" * 60)
        print("                         REPOLENS")
        print("=" * 60)

        print("\n" + answer)

        print("\n" + "=" * 60)

        return True

    except Exception as error:

        print("\n❌ RepoLens encountered an error.")

        print("\nError details:")
        print(error)

        return False


def main():

    print_header()

    print(
        "\nRepoLens analyzes GitHub repositories using:"
        "\n• MCP"
        "\n• GitHub API"
        "\n• Python data analysis"
        "\n• Qwen3 local LLM"
    )

    while True:

        owner, repo = get_repository()

        question = get_question()

        success = run_analysis(
            owner,
            repo,
            question
        )

        print("\n")

        if success:

            again = input(
                "Analyze another repository? (y/n): "
            ).strip().lower()

        else:

            again = input(
                "Try another repository? (y/n): "
            ).strip().lower()

        if again != "y":

            print(
                "\nThank you for using RepoLens. 🔎"
            )

            break


if __name__ == "__main__":
    main()