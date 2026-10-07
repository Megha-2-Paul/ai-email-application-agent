from __future__ import annotations

import re
from typing import Any


DATA_ANALYST_RESUME = "Data Analyst Resume"
PYTHON_DEVELOPER_RESUME = "Python Developer Resume"

_DATA_ROLE_PATTERNS = (
    "data analyst",
    "data analytics",
    "business intelligence",
    "bi analyst",
    "mis analyst",
    "mis executive",
    "reporting analyst",
    "sql analyst",
    "data scientist",
    "data science",
    "data engineer",
)

_PYTHON_ROLE_PATTERNS = (
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

_DATA_REQUIREMENT_KEYWORDS = (
    "power bi",
    "tableau",
    "kpi analysis",
    "dashboard",
    "data visualization",
    "reporting",
    "sql",
    "excel",
    "analytics",
)

_PYTHON_REQUIREMENT_KEYWORDS = (
    "python",
    "fastapi",
    "flask",
    "django",
    "rest api",
    "api development",
    "docker",
    "rag",
    "llm",
    "genai",
    "generative ai",
    "machine learning",
    "tensorflow",
    "pytorch",
    "hugging face",
)


def _text(row: dict[str, Any], keys: tuple[str, ...]) -> str:
    return " ".join(
        str(row.get(key, "") or "").strip().lower()
        for key in keys
    )


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern in text for pattern in patterns)


def select_resume_type(row: dict[str, Any]) -> str:
    """Select a resume using explicit role signals before requirement scoring.

    Role titles and role families are stronger signals than individual
    requirement keywords. This prevents data-related terms in a Python/AI
    posting from incorrectly switching the resume to the analytics version.
    """
    role_text = _text(row, ("Current Role", "Role Family"))

    if _contains_any(role_text, _PYTHON_ROLE_PATTERNS):
        return PYTHON_DEVELOPER_RESUME

    if _contains_any(role_text, _DATA_ROLE_PATTERNS):
        return DATA_ANALYST_RESUME

    requirements = _text(
        row,
        ("Job Description / Requirements", "Notes"),
    )
    python_score = sum(
        requirements.count(keyword) for keyword in _PYTHON_REQUIREMENT_KEYWORDS
    )
    data_score = sum(
        requirements.count(keyword) for keyword in _DATA_REQUIREMENT_KEYWORDS
    )

    if data_score > python_score:
        return DATA_ANALYST_RESUME

    return PYTHON_DEVELOPER_RESUME
