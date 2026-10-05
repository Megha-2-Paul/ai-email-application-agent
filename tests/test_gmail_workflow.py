import pandas as pd
import pytest

import gmail_workflow


class FakeGmailService:
    def __init__(self):
        self.created = []
        self.sent = []

    def create_draft(self, to, subject, body):
        self.created.append((to, subject, body))
        return f"draft-{len(self.created)}"

    def send_draft(self, draft_id):
        self.sent.append(draft_id)
        return f"message-{draft_id}"


def test_send_requires_confirmation(tmp_path):
    path = tmp_path / "input.csv"
    pd.DataFrame([
        {
            "Company": "Example",
            "Current Role": "Python Developer",
            "Job Description / Requirements": "Python",
            "Public Email": "person@example.com",
            "Gmail Draft ID": "draft-1",
            "Gmail Approval": "Approved",
        }
    ]).to_csv(path, index=False)

    with pytest.raises(ValueError, match="--confirm"):
        gmail_workflow.send_approved(
            str(path), str(tmp_path / "output.csv"), confirm=False
        )


def test_create_drafts_creates_only_valid_unique_generated_rows(monkeypatch, tmp_path):
    fake = FakeGmailService()
    monkeypatch.setattr(gmail_workflow, "GmailService", lambda: fake)

    path = tmp_path / "input.csv"
    output = tmp_path / "output.csv"
    pd.DataFrame([
        {
            "Company": "Example",
            "Current Role": "Python Developer",
            "Job Description / Requirements": "Python",
            "Public Email": "person@example.com",
            "Generated Subject": "Python Developer Application",
            "Generated Email": "Hello, I would like to apply.",
            "Generation Status": "Generated",
        },
        {
            "Company": "Example",
            "Current Role": "Python Developer",
            "Job Description / Requirements": "Python",
            "Public Email": "person@example.com",
            "Generated Subject": "Python Developer Application",
            "Generated Email": "Duplicate application.",
            "Generation Status": "Generated",
        },
        {
            "Company": "Bad",
            "Current Role": "Python Developer",
            "Job Description / Requirements": "Python",
            "Public Email": "not-an-email",
            "Generated Subject": "Application",
            "Generated Email": "Hello.",
            "Generation Status": "Generated",
        },
    ]).to_csv(path, index=False)

    gmail_workflow.create_drafts(str(path), str(output))

    result = pd.read_csv(output).fillna("")
    assert fake.created == [
        (
            "person@example.com",
            "Python Developer Application",
            "Hello, I would like to apply.",
        )
    ]
    assert result.loc[0, "Gmail Draft ID"] == "draft-1"
    assert result.loc[0, "Gmail Approval"] == "Pending Review"
    assert result.loc[1, "Gmail Draft Status"] == "Duplicate Skipped"
    assert result.loc[2, "Gmail Draft Status"] == "Invalid Email"


def test_send_sends_only_approved_unsent_rows(monkeypatch, tmp_path):
    fake = FakeGmailService()
    monkeypatch.setattr(gmail_workflow, "GmailService", lambda: fake)

    path = tmp_path / "input.csv"
    output = tmp_path / "output.csv"
    pd.DataFrame([
        {
            "Company": "Approved",
            "Current Role": "Python Developer",
            "Job Description / Requirements": "Python",
            "Public Email": "one@example.com",
            "Gmail Draft ID": "draft-1",
            "Gmail Approval": "Approved",
            "Gmail Send Status": "",
        },
        {
            "Company": "Pending",
            "Current Role": "Python Developer",
            "Job Description / Requirements": "Python",
            "Public Email": "two@example.com",
            "Gmail Draft ID": "draft-2",
            "Gmail Approval": "Pending Review",
            "Gmail Send Status": "",
        },
        {
            "Company": "Already Sent",
            "Current Role": "Python Developer",
            "Job Description / Requirements": "Python",
            "Public Email": "three@example.com",
            "Gmail Draft ID": "draft-3",
            "Gmail Approval": "Approved",
            "Gmail Send Status": "Sent (message-old)",
        },
    ]).to_csv(path, index=False)

    gmail_workflow.send_approved(
        str(path), str(output), confirm=True
    )

    result = pd.read_csv(output).fillna("")
    assert fake.sent == ["draft-1"]
    assert result.loc[0, "Gmail Send Status"] == "Sent (message-draft-1)"
    assert result.loc[0, "Gmail Draft Status"] == "Sent"
    assert result.loc[1, "Gmail Send Status"] == ""
    assert result.loc[2, "Gmail Send Status"] == "Sent (message-old)"


def test_send_records_gmail_errors(monkeypatch, tmp_path):
    class FailingGmailService(FakeGmailService):
        def send_draft(self, draft_id):
            raise RuntimeError("temporary Gmail failure")

    monkeypatch.setattr(gmail_workflow, "GmailService", FailingGmailService)

    path = tmp_path / "input.csv"
    output = tmp_path / "output.csv"
    pd.DataFrame([
        {
            "Company": "Example",
            "Current Role": "Python Developer",
            "Job Description / Requirements": "Python",
            "Public Email": "person@example.com",
            "Gmail Draft ID": "draft-1",
            "Gmail Approval": "Approved",
        }
    ]).to_csv(path, index=False)

    gmail_workflow.send_approved(
        str(path), str(output), confirm=True
    )

    result = pd.read_csv(output).fillna("")
    assert result.loc[0, "Gmail Send Status"] == "Send failed: temporary Gmail failure"
    assert result.loc[0, "Gmail Draft Status"] == ""


def test_create_drafts_records_gmail_errors(monkeypatch, tmp_path):
    class FailingGmailService(FakeGmailService):
        def create_draft(self, to, subject, body):
            raise RuntimeError("draft service unavailable")

    monkeypatch.setattr(gmail_workflow, "GmailService", FailingGmailService)

    path = tmp_path / "input.csv"
    output = tmp_path / "output.csv"
    pd.DataFrame([
        {
            "Company": "Example",
            "Current Role": "Python Developer",
            "Job Description / Requirements": "Python",
            "Public Email": "person@example.com",
            "Generated Subject": "Application",
            "Generated Email": "Hello.",
            "Generation Status": "Generated",
        }
    ]).to_csv(path, index=False)

    gmail_workflow.create_drafts(str(path), str(output))

    result = pd.read_csv(output).fillna("")
    assert result.loc[0, "Gmail Draft Status"] == "Error"
    assert result.loc[0, "Gmail Send Status"] == "Draft creation failed: draft service unavailable"
