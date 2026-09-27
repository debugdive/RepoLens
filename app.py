import asyncio
import streamlit as st

from agent import analyze_with_agent


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="RepoLens",
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🔎 RepoLens")

st.subheader(
    "Autonomous Software Repository Investigator"
)

st.write(
    "RepoLens uses MCP, GitHub data, Python analysis, "
    "and a local Qwen3 model to investigate software repositories."
)

st.divider()


# ============================================================
# INPUTS
# ============================================================

st.markdown("### Repository")

repository = st.text_input(
    "GitHub repository",
    placeholder="microsoft/vscode"
)

st.markdown("### Investigation")

question = st.text_area(
    "What should RepoLens investigate?",
    placeholder=(
        "Which areas of this repository should be "
        "investigated first?"
    ),
    height=100
)


# ============================================================
# EXAMPLES
# ============================================================

st.markdown("### Example questions")

example = st.selectbox(
    "Choose an example",
    [
        "Which areas of this repository should be investigated first?",
        "How many stale issues are currently present?",
        "How active is recent development?",
        "Is contributor activity concentrated?",
        "What potential engineering concerns should be investigated?"
    ]
)

if st.button("Use Example"):
    question = example
    st.rerun()


# ============================================================
# INVESTIGATE BUTTON
# ============================================================

if st.button(
    "🔍 Investigate Repository",
    type="primary",
    use_container_width=True
):

    if not repository:
        st.error(
            "Please enter a GitHub repository."
        )

    elif "/" not in repository:
        st.error(
            "Use the format: owner/repository"
        )

    elif not question:
        st.error(
            "Please enter an investigation question."
        )

    else:

        parts = repository.strip("/ ").split("/")

        if len(parts) != 2:

            st.error(
                "Use the format: owner/repository"
            )

        else:

            owner = parts[0]
            repo = parts[1]

            # ------------------------------------------------
            # RUN AGENT
            # ------------------------------------------------

            with st.spinner(
                "RepoLens is investigating the repository..."
            ):

                try:

                    result = asyncio.run(
                        analyze_with_agent(
                            owner,
                            repo,
                            question
                        )
                    )

                except Exception as error:

                    st.error(
                        f"RepoLens encountered an error: {error}"
                    )

                    st.stop()


            # ------------------------------------------------
            # GET RESULTS
            # ------------------------------------------------

            selected_tools = result[
                "selected_tools"
            ]

            analysis = result[
                "analysis"
            ]

            answer = result[
                "answer"
            ]


            # =================================================
            # AGENT DECISION
            # =================================================

            st.divider()

            st.markdown(
                "## 🤖 Agent Decision"
            )

            st.write(
                "RepoLens selected these MCP tools:"
            )

            for tool in selected_tools:
                st.code(tool)


            # =================================================
            # REPOSITORY OVERVIEW
            # =================================================

            st.markdown(
                "## 📦 Repository Overview"
            )

            overview_col1, overview_col2 = st.columns(2)

            with overview_col1:

                st.write(
                    "**Repository:**",
                    analysis.get(
                        "repository",
                        "Unknown"
                    )
                )

                st.write(
                    "**Language:**",
                    analysis.get(
                        "language",
                        "Unknown"
                    )
                )

            with overview_col2:

                st.write(
                    "**Stars:**",
                    analysis.get(
                        "stars",
                        0
                    )
                )

                st.write(
                    "**Forks:**",
                    analysis.get(
                        "forks",
                        0
                    )
                )


            # =================================================
            # ENGINEERING METRICS
            # =================================================

            st.markdown(
                "## 📊 Engineering Metrics"
            )

            metrics = analysis.get(
                "metrics",
                {}
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Issues Retrieved",
                    metrics.get(
                        "open_issues_retrieved",
                        0
                    )
                )

            with col2:
                st.metric(
                    "PRs Retrieved",
                    metrics.get(
                        "open_pull_requests_retrieved",
                        0
                    )
                )

            with col3:
                st.metric(
                    "Recent Commits",
                    metrics.get(
                        "recent_commits_retrieved",
                        0
                    )
                )

            with col4:
                st.metric(
                    "Stale Issues",
                    metrics.get(
                        "stale_issues",
                        0
                    )
                )


            # =================================================
            # ENGINEERING SIGNALS
            # =================================================

            st.markdown(
                "## 🚦 Engineering Signals"
            )

            signals = analysis.get(
                "signals",
                {}
            )

            sig1, sig2 = st.columns(2)

            with sig1:

                st.write(
                    "**Development Activity:**",
                    signals.get(
                        "development_activity",
                        "Unknown"
                    )
                )

                st.write(
                    "**Issue Backlog:**",
                    signals.get(
                        "issue_backlog",
                        "Unknown"
                    )

                )

                st.write(
                    "**Pull Request Activity:**",
                    signals.get(
                        "pull_request_activity",
                        "Unknown"
                    )
                )

            with sig2:

                st.write(
                    "**Contributor Concentration:**",
                    signals.get(
                        "contributor_concentration",
                        "Unknown"
                    )
                )

                st.write(
                    "**Stale Issue Level:**",
                    signals.get(
                        "stale_issue_level",
                        "Unknown"
                    )
                )


            # =================================================
            # AI INVESTIGATION
            # =================================================

            st.divider()

            st.markdown(
                "## 🧠 RepoLens Investigation"
            )

            st.markdown(
                answer
            )


            # =================================================
            # LIMITATION
            # =================================================

            st.divider()

            st.caption(
                "Analysis is based on the GitHub records retrieved "
                "by the current MCP tools and represents the "
                "retrieved sample rather than the complete "
                "repository history."
            )