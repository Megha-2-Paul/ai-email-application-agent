from pathlib import Path

from app.gmail_service import GmailService


def test_message_includes_pdf_attachment(tmp_path):
    resume = tmp_path / "resume.pdf"
    resume.write_bytes(b"%PDF-test")

    payload = GmailService._message(
        "person@example.com",
        "Application",
        "Hello",
        attachments=[resume],
    )

    raw = payload["raw"]
    assert raw
    assert "resume.pdf" in __import__("base64").urlsafe_b64decode(raw).decode(
        "utf-8", errors="ignore"
    )


def test_message_rejects_missing_attachment(tmp_path):
    missing = tmp_path / "missing.pdf"

    try:
        GmailService._message(
            "person@example.com",
            "Application",
            "Hello",
            attachments=[missing],
        )
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError")
