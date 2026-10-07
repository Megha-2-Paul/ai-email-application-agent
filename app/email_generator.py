import json
import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


@dataclass(frozen=True)
class CandidateProfile:
    name: str = "Megha Paul"
    current_role: str = "Associate Data Analyst"
    experience: str = "2 years"
    location: str = "Kolkata, India"
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


def _clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value != value:
        return ""
    return str(value).strip()


class EmailGenerator:
    def __init__(self, model: str | None = None, client: Groq | None = None):
        api_key = os.getenv("GROQ_API_KEY")
        if client is not None:
            self.client = client
        elif api_key:
            self.client = Groq(api_key=api_key)
        else:
            raise ValueError("GROQ_API_KEY is not configured.")
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    @staticmethod
    def build_user_prompt(row: dict[str, Any], profile: CandidateProfile) -> str:
        candidate = {
            "name": profile.name,
            "current_role": profile.current_role,
            "experience": profile.experience,
            "location": profile.location,
            "skills": list(profile.skills),
            "relevant_projects": list(profile.relevant_projects),
        }
        job = {
            "company": _clean(row.get("Company")),
            "role": _clean(row.get("Current Role")),
            "role_family": _clean(row.get("Role Family")),
            "work_location": _clean(row.get("Work Location")),
            "work_mode": _clean(row.get("Work Mode")),
            "experience": _clean(row.get("Experience")),
            "employment_type": _clean(row.get("Employment Type")),
            "requirements": _clean(row.get("Job Description / Requirements")),
            "recruiter": _clean(row.get("Recruiter / Contact")),
            "job_url": _clean(row.get("Job / Apply URL")),
            "notes": _clean(row.get("Notes")),
        }
        return (
            "Create an application email using these facts.\n\n"
            f"CANDIDATE PROFILE:\n{json.dumps(candidate, indent=2)}\n\n"
            f"JOB INFORMATION:\n{json.dumps(job, indent=2)}"
        )

    def generate(
        self,
        row: dict[str, Any],
        profile: CandidateProfile | None = None,
    ) -> tuple[str, str]:
        profile = profile or CandidateProfile()
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You write concise professional job application emails. "
                        "Return exactly two sections with these labels: "
                        "SUBJECT: and BODY:. Do not invent candidate facts, "
                        "salary, notice period, qualifications, or job details."
                    ),
                },
                {"role": "user", "content": self.build_user_prompt(row, profile)},
            ],
        )
        content = response.choices[0].message.content
        if not content or not content.strip():
            raise ValueError("Groq returned an empty response.")
        return self._parse_response(content.strip())

    @staticmethod
    def _parse_response(content: str) -> tuple[str, str]:
        cleaned = content.strip()
        if cleaned.startswith("\`\`\`") and cleaned.endswith("\`\`\`"):
            cleaned = "\n".join(cleaned.splitlines()[1:-1]).strip()

        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        subject_index = next(
            (
                i
                for i, line in enumerate(lines)
                if line.lstrip("#*_- ").upper().startswith("SUBJECT:")
            ),
            None,
        )
        body_index = next(
            (
                i
                for i, line in enumerate(lines)
                if line.lstrip("#*_- ").upper().startswith("BODY:")
            ),
            None,
        )

        if subject_index is None or body_index is None or body_index <= subject_index:
            raise ValueError("Groq response must contain SUBJECT: followed by BODY:.")

        subject_line = lines[subject_index].lstrip("#*_- ").strip()
        body_start = lines[body_index].lstrip("#*_- ").strip()
        subject = subject_line.split(":", 1)[1].strip()
        body = "\n".join(
            [body_start.split(":", 1)[1].strip(), *lines[body_index + 1 :]]
        ).strip()

        if not subject:
            raise ValueError("Groq returned an empty subject.")
        if not body:
            raise ValueError("Groq returned an empty body.")

        return subject, body
