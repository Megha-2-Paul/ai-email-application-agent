import json
from typing import Any

from groq import Groq

from .config import CandidateProfile, get_groq_api_key, get_groq_model


SYSTEM_PROMPT = """You write concise, professional cold-application emails for job seekers.

Rules:
- Never invent qualifications, employers, years of experience, projects, tools, degrees, or achievements.
- Use only facts supplied in the candidate profile and job row.
- Personalize the email to the role and company.
- Mention only candidate skills/projects relevant to the role.
- Do not mention salary, relocation, or notice period unless supplied in the job row.
- Do not claim to have spoken with the recruiter.
- Keep the email around 120-180 words.
- Use a professional, natural tone and avoid buzzword-heavy language.
- If a contact name is provided, address them by name. Otherwise use "Dear Hiring Team,".
- Return valid JSON with exactly two keys: "subject" and "body".
"""


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


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
        "Create an application email using these facts.

"
        f"CANDIDATE PROFILE:
{json.dumps(candidate, indent=2)}

"
        f"JOB INFORMATION:
{json.dumps(job, indent=2)}"
    )


class EmailGenerator:
    def __init__(self, client: Groq | None = None, model: str | None = None):
        self.client = client or Groq(api_key=get_groq_api_key())
        self.model = model or get_groq_model()

    def generate(self, row: dict[str, Any]) -> tuple[str, str]:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.25,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(row, CandidateProfile())},
            ],
        )
        content = response.choices[0].message.content or "{}"
        payload = json.loads(content)
        subject = _clean(payload.get("subject"))
        body = _clean(payload.get("body"))
        if not subject or not body:
            raise ValueError("Groq returned an incomplete email.")
        return subject, body
