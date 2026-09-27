# 🔎 RepoLens

### Autonomous Software Repository Investigator

RepoLens is an MCP-powered GenAI application that investigates GitHub repositories using repository data, engineering metrics, and a local Qwen3 model.

##  What It Does

Give RepoLens a GitHub repository and a question. It:

1. Uses Qwen3 to select the relevant MCP tools.
2. Retrieves repository data from GitHub.
3. Analyzes engineering signals using Python.
4. Uses Qwen3 to interpret the evidence.
5. Displays the investigation in a Streamlit UI.

##  Architecture

```text
User
 ↓
Streamlit UI
 ↓
Qwen3 Planner
 ↓
MCP Tool Selection
 ↓
GitHub MCP Server
 ↓
Repository Data
 ↓
Python Analyzer
 ↓
Qwen3 Investigator
 ↓
Investigation Report
