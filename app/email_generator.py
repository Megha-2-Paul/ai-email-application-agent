import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from app.config import CandidateProfile, PROFILE

load_dotenv()


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
            "Create a concise professional application email using only the "
            "candidate facts explicitly provided below. Use the job information "
            "only to understand the role and decide which candidate facts are "
            "relevant. Job requirements are NOT candidate experience or skills. "
            "Never claim that the candidate has a tool, qualification, project, "
            "deployment experience, cloud experience, or other capability unless "
            "it appears in CANDIDATE PROFILE. Do not invent salary, notice period, "
            "education, years of experience, employer details, or achievements. "
            "Do not say that the candidate has completed a job requirement merely "
            "because the requirement appears in the posting. Keep the email "
            "specific but factual. Do not add a greeting sign-off or contact "
            "signature beyond the email body itself; the application system adds "
            "the final signature.\n\n"
            f"CANDIDATE PROFILE:\n{json.dumps(candidate, indent=2)}\n\n"
            f"JOB INFORMATION:\n{json.dumps(job, indent=2)}"
        )

    @staticmethod
    def _signature(profile: CandidateProfile) -> str:
        return (
            "\n\nBest regards,\n"
            f"{profile.name}\n"
            f"{profile.current_role}\n"
            f"{profile.phone}\n"
            f"{profile.email}\n"
            f"LinkedIn: {profile.linkedin_url}"
        )

    @staticmethod
    def _clean_body(body: str) -> str:
        lines = [line.rstrip() for line in body.strip().splitlines()]

        closing_pattern = re.compile(
            r"^(best regards|kind regards|regards|sincerely|warm regards|"
            r"thanks and regards|thank you|best)\s*[,!:.]*$",
            re.IGNORECASE,
        )

        while lines and not lines[-1].strip():
            lines.pop()

        for index in range(len(lines) - 1, -1, -1):
            if not lines[index].strip():
                continue
            if closing_pattern.match(lines[index].strip()):
                lines = lines[:index]
                break

        while lines and not lines[-1].strip():
            lines.pop()

        cleaned_lines = [line.strip() for line in lines]
        return "\n".join(cleaned_lines).strip()

    def generate(
        self,
        row: dict[str, Any],
        profile: CandidateProfile | None = None,
    ) -> tuple[str, str]:
        profile = profile or PROFILE
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You write concise professional job application emails. "
                        "Return only two sections, each starting on its own line: "
                        "SUBJECT: <one-line subject> and BODY: <email body>. "
                        "Do not use Markdown headings, code fences, or extra labels. "
                        "Do not add a signature or contact details; those are added "
                        "by the application system. "
                        "The candidate profile is the only source of candidate "
                        "facts. Treat every job requirement as a requirement of the "
                        "employer, not as proof that the candidate has that skill. "
                        "Never invent candidate facts, salary, notice period, "
                        "qualifications, experience, tools, projects, or job details."
                    ),
                },
                {"role": "user", "content": self.build_user_prompt(row, profile)},
            ],
        )
        content = response.choices[0].message.content
        if not content or not content.strip():
            raise ValueError("Groq returned an empty response.")

        subject, body = self._parse_response(content.strip())
        body = self._clean_body(body)
        if not body:
            raise ValueError("Groq returned an empty body.")
        return subject, body + self._signature(profile)

    @staticmethod
    def _parse_response(content: str) -> tuple[str, str]:
        cleaned = content.strip()
        if cleaned.startswith(chr(96) * 3) and cleaned.endswith(chr(96) * 3):
            cleaned = "\n".join(cleaned.splitlines()[1:-1]).strip()

        lines = cleaned.splitlines()
        subject_index = next(
            (
                i
                for i, line in enumerate(lines)
                if line.strip().lstrip("#*_- ").upper().startswith("SUBJECT:")
            ),
            None,
        )
        body_index = next(
            (
                i
                for i, line in enumerate(lines)
                if line.strip().lstrip("#*_- ").upper().startswith("BODY:")
            ),
            None,
        )

        if subject_index is None or body_index is None or body_index <= subject_index:
            raise ValueError("Groq response must contain SUBJECT: followed by BODY:.")

        subject_line = lines[subject_index].strip().lstrip("#*_- ").strip()
        body_start = lines[body_index].strip().lstrip("#*_- ").strip()
        subject = subject_line.split(":", 1)[1].strip()
        body_lines = [
            body_start.split(":", 1)[1].strip(),
            *lines[body_index + 1 :],
        ]
        body = "\n".join(body_lines).strip()

        if not subject:
            raise ValueError("Groq returned an empty subject.")
        if not body:
            raise ValueError("Groq returned an empty body.")

        return subject, body
