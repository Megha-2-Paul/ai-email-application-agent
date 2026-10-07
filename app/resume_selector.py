from __future__ import annotations

from typing import Any


DATA_ANALYST_RESUME = "Data Analyst Resume"
PYTHON_DEVELOPER_RESUME = "Python Developer Resume"

_DATA_KEYWORDS = (
    "data analyst",
    "data analytics",
    "business intelligence",
    "bi analyst",
    "mis analyst",
    "mis executive",
    "reporting analyst",
    "sql analyst",
    "power bi",
    "data scientist",
    "data science",
    "data engineer",
    "analytics",
)

_PYTHON_KEYWORDS = (
    "python developer",
    "python backend",
    "backend developer",
    "backend engineer",
    "fastapi",
    "api developer",
    "ai engineer",
    "ai/ml engineer",
    "ai developer",
    "ai application",
    "ml engineer",
    "machine learning engineer",
    "generative ai",
    "genai",
    "rag",
    "llm",
    "artificial intelligence",
    "nlp",
)


def select_resume_type(row: dict[str, Any]) -> str:
    text = " ".join(
        str(row.get(key, "") or "").lower()
        for key in (
            "Current Role",
            "Role Family",
            "Job Description / Requirements",
            "Notes",
        )
    )

    data_score = sum(text.count(keyword) for keyword in _DATA_KEYWORDS)
    python_score = sum(text.count(keyword) for keyword in _PYTHON_KEYWORDS)

    if data_score > python_score:
        return DATA_ANALYST_RESUME
    return PYTHON_DEVELOPER_RESUME
