import requests
import json


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:1.7b"


def generate_insight(analysis, question):
    """Generate a short repository investigation using Qwen3."""

    compact_analysis = {
        "repository": analysis.get("repository"),
        "metrics": analysis.get("metrics", {}),
        "signals": analysis.get("signals", {}),
        "investigation_signals": analysis.get(
            "investigation_signals",
            []
        )
    }

    prompt = f"""
You are RepoLens, a software repository investigator.

Repository evidence:
{json.dumps(compact_analysis)}

Question:
{question}
Strict evidence rules:
- Potential concerns MUST be supported by the provided evidence.
- If stale_issues is 0 or stale_issue_ratio_percent is 0,
  NEVER say that stale issues are a concern.
- Never infer code quality problems from contributor concentration
  or commit timing alone.
- If the evidence does not support a concern, say:
  "No major concern detected from the retrieved sample."

Give ONLY this format:

CONCERN:
<one potential concern>

EVIDENCE:
- <fact>
- <fact>

NEXT:
<one investigation to perform>

Do not invent facts.
Keep the answer under 80 words.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,

                # IMPORTANT:
                # Disable Qwen3 thinking for faster direct answers.
                "think": False,

                "options": {
                    "temperature": 0.2,
                    "num_predict": 80
                }
            },
            timeout=60
        )

        if response.status_code != 200:
            return f"Ollama error: {response.text}"

        data = response.json()

        answer = data.get("response", "").strip()

        if not answer:
            # Useful fallback if Ollama ever returns
            # an empty final response.
            return (
                "CONCERN:\n"
                "No AI-generated concern was returned.\n\n"
                "EVIDENCE:\n"
                "- Repository analysis completed.\n"
                "- Engineering signals were calculated.\n\n"
                "NEXT:\n"
                "Inspect the repository signals manually."
            )

        return answer

    except requests.exceptions.ConnectionError:
        return (
            "Could not connect to Ollama. "
            "Make sure Ollama is running."
        )

    except requests.exceptions.Timeout:
        return (
            "Qwen3 timed out. "
            "The local model may be running slowly."
        )

    except Exception as error:
        return f"LLM error: {error}"


if __name__ == "__main__":
    print("RepoLens LLM module loaded successfully.")