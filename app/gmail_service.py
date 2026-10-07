import base64
import mimetypes
from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


class GmailService:
    def __init__(self, credentials_path="credentials.json", token_path="token.json"):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self._service = None

    def authenticate(self):
        creds = None
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"OAuth client file not found: {self.credentials_path}"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            self.token_path.write_text(creds.to_json(), encoding="utf-8")

        self._service = build("gmail", "v1", credentials=creds)
        return self._service

    @property
    def service(self):
        return self._service or self.authenticate()

    @staticmethod
    def _message(to, subject, body, attachments=None):
        message = EmailMessage()
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        for attachment in attachments or []:
            path = Path(attachment)
            if not path.exists() or not path.is_file():
                raise FileNotFoundError(f"Attachment not found: {path}")

            content_type, _ = mimetypes.guess_type(path.name)
            maintype, subtype = (content_type or "application/octet-stream").split(
                "/", 1
            )
            message.add_attachment(
                path.read_bytes(),
                maintype=maintype,
                subtype=subtype,
                filename=path.name,
            )

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {"raw": raw}

    def create_draft(self, to, subject, body, attachments=None):
        draft = self.service.users().drafts().create(
            userId="me",
            body={"message": self._message(to, subject, body, attachments)},
        ).execute()
        return draft["id"]

    def send_draft(self, draft_id):
        message = self.service.users().drafts().send(
            userId="me",
            body={"id": draft_id},
        ).execute()
        return message["id"]
