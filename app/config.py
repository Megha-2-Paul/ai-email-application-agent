from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class CandidateProfile:
    name: str = "Megha Paul"
    current_role: str = "Associate Data Analyst"
    experience: str = "2 years of professional experience"
    location: str = "Kolkata, India"
    skills: tuple[str, ...] = (
        "Python", "SQL", "Pandas", "NumPy", "scikit-learn",
        "FastAPI", "REST APIs", "Git", "GitHub", "Excel",
        "data analytics", "machine learning", "AI/LLM projects",
    )
    relevant_projects: tuple[str, ...] = (
        "AI Data Analyst Agent",
        "Mathematics Assessment and Improvement System",
    )


PROFILE = CandidateProfile()


def get_groq_api_key() -> str:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return key


def get_groq_model() -> str:
    return os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
