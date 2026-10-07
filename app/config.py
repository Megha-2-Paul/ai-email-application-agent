from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class CandidateProfile:
    name: str = "Megha Paul"
    current_role: str = "Associate Data Analyst"
    experience: str = "2 years"
    location: str = "Kolkata, India"
    email: str = "meghapaul0202@gmail.com"
    phone: str = "+91 6289771661"
    linkedin_url: str = "https://www.linkedin.com/in/megha-paul-735bb1298"
    skills: tuple[str, ...] = (
        "Python",
        "SQL",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "FastAPI",
        "Git",
        "GitHub",
        "Data Analysis",
        "Machine Learning",
    )
    relevant_projects: tuple[str, ...] = (
        "AI Data Analyst Agent",
        "IoT & ML project",
        "COVID-19 dashboard",
        "Mental health dataset analysis",
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
    return os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
