from types import SimpleNamespace

import pytest

from app.config import PROFILE
from app.email_generator import CandidateProfile, EmailGenerator


class FakeGroqClient:
    def __init__(self, content):
        self.content = content
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self.create)
        )
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))]
        )


def test_parse_response():
    subject, body = EmailGenerator._parse_response(
        "SUBJECT: Python Developer Application\n"
        "BODY: Hello Hiring Team,\n"
        "I would like to apply: please find my profile attached."
    )

    assert subject == "Python Developer Application"
    assert body == (
        "Hello Hiring Team,\n"
        "I would like to apply: please find my profile attached."
    )


@pytest.mark.parametrize(
    "content",
    [
        "",
        "SUBJECT: Only subject",
        "BODY: Only body",
        "BODY: Body first\nSUBJECT: Subject",
        "SUBJECT:\nBODY: Body",
        "SUBJECT: Subject\nBODY:",
    ],
)
def test_parse_response_rejects_invalid_output(content):
    with pytest.raises(ValueError):
        EmailGenerator._parse_response(content)


def test_parse_response_tolerates_markdown_headings():
    subject, body = EmailGenerator._parse_response(
        "### SUBJECT: Python Developer Application\n"
        "### BODY: Hello Hiring Team,\n"
        "I am applying."
    )
    assert subject == "Python Developer Application"
    assert body == "Hello Hiring Team,\nI am applying."


def test_parse_response_tolerates_code_fences():
    fence = chr(96) * 3
    subject, body = EmailGenerator._parse_response(
        f"{fence}\nSUBJECT: Python Developer Application\n"
        f"BODY: Hello Hiring Team,\nI am applying.\n{fence}"
    )
    assert subject == "Python Developer Application"
    assert body == "Hello Hiring Team,\nI am applying."


def test_generate_uses_fake_groq_client():
    client = FakeGroqClient(
        "SUBJECT: Data Analyst Application\n"
        "BODY: Hello Hiring Team,\n"
        "I am applying for this opportunity."
    )
    generator = EmailGenerator(model="test-model", client=client)

    subject, body = generator.generate(
        {
            "Company": "Example",
            "Current Role": "Data Analyst",
            "Job Description / Requirements": "Python and SQL",
        },
        profile=CandidateProfile(),
    )

    assert subject == "Data Analyst Application"
    assert body.endswith(
        "Best regards,\n"
        "Megha Paul\n"
        "Associate Data Analyst\n"
        "+91 6289771661\n"
        "meghapaul0202@gmail.com\n"
        "LinkedIn: https://www.linkedin.com/in/megha-paul-735bb1298"
    )
    assert client.calls[0]["model"] == "test-model"
    assert client.calls[0]["temperature"] == 0.2


def test_default_profile_has_contact_details():
    assert PROFILE.email == "meghapaul0202@gmail.com"
    assert PROFILE.phone == "+91 6289771661"
    assert PROFILE.linkedin_url == "https://www.linkedin.com/in/megha-paul-735bb1298"


def test_default_model_is_current_groq_model(monkeypatch):
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    generator = EmailGenerator(client=FakeGroqClient("SUBJECT: Test\nBODY: Test body"))
    assert generator.model == "openai/gpt-oss-120b"


def test_generate_rejects_empty_groq_response():
    client = FakeGroqClient("")
    generator = EmailGenerator(client=client)

    with pytest.raises(ValueError, match="empty response"):
        generator.generate({"Company": "Example"})
