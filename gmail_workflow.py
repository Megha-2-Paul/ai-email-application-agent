import argparse
import re
from pathlib import Path

from app.excel_reader import load_job_sheet, write_output
from app.gmail_service import GmailService

APPROVED = "Approved"
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def ensure_gmail_columns(df):
    for column in (
        "Gmail Draft ID",
        "Gmail Draft Status",
        "Gmail Approval",
        "Gmail Send Status",
    ):
        if column not in df.columns:
            df[column] = ""
    return df


def _valid_email(value):
    return bool(EMAIL_PATTERN.match(str(value).strip()))


def create_drafts(input_path, output_path, sheet_name="Qualified Leads"):
    df = ensure_gmail_columns(load_job_sheet(input_path, sheet_name))
    required = {"Generated Subject", "Generated Email", "Public Email"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

    gmail = GmailService()
    created = 0
    seen_keys = set()

    for index, row in df.iterrows():
        if str(row.get("Gmail Draft ID", "")).strip():
            continue
        if str(row.get("Generation Status", "")).strip() != "Generated":
            continue

        to = str(row["Public Email"]).strip()
        subject = str(row["Generated Subject"]).strip()
        body = str(row["Generated Email"]).strip()

        if not to or not subject or not body:
            df.at[index, "Gmail Draft Status"] = "Skipped"
            df.at[index, "Gmail Send Status"] = "Missing email, subject, or body"
            continue

        if not _valid_email(to):
            df.at[index, "Gmail Draft Status"] = "Invalid Email"
            df.at[index, "Gmail Send Status"] = f"Invalid email address: {to}"
            continue

        draft_key = (to.lower(), subject)
        if draft_key in seen_keys:
            df.at[index, "Gmail Draft Status"] = "Duplicate Skipped"
            df.at[index, "Gmail Send Status"] = (
                "Duplicate recipient and subject in this batch"
            )
            continue

        seen_keys.add(draft_key)

        try:
            draft_id = gmail.create_draft(to, subject, body)
            df.at[index, "Gmail Draft ID"] = draft_id
            df.at[index, "Gmail Draft Status"] = "Created"
            df.at[index, "Gmail Approval"] = "Pending Review"
            df.at[index, "Gmail Send Status"] = ""
            created += 1
        except Exception as exc:
            df.at[index, "Gmail Draft Status"] = "Error"
            df.at[index, "Gmail Send Status"] = f"Draft creation failed: {exc}"

    write_output(input_path, output_path, df, sheet_name=sheet_name)
    print(f"Drafts created: {created}")
    print(f"Output: {Path(output_path).resolve()}")


def send_approved(input_path, output_path, sheet_name="Qualified Leads", confirm=False):
    if not confirm:
        raise ValueError("Sending requires --confirm. This prevents accidental sends.")

    df = load_job_sheet(input_path, sheet_name)
    required = {"Gmail Draft ID", "Gmail Approval"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

    if "Gmail Send Status" not in df.columns:
        df["Gmail Send Status"] = ""
    if "Gmail Draft Status" not in df.columns:
        df["Gmail Draft Status"] = ""

    gmail = GmailService()
    sent = 0

    for index, row in df.iterrows():
        approval = str(row.get("Gmail Approval", "")).strip()
        draft_id = str(row.get("Gmail Draft ID", "")).strip()
        status = str(row.get("Gmail Send Status", "")).strip()

        if approval != APPROVED or not draft_id or status.startswith("Sent"):
            continue

        try:
            message_id = gmail.send_draft(draft_id)
            df.at[index, "Gmail Send Status"] = f"Sent ({message_id})"
            df.at[index, "Gmail Draft Status"] = "Sent"
            sent += 1
        except Exception as exc:
            df.at[index, "Gmail Send Status"] = f"Send failed: {exc}"

    write_output(input_path, output_path, df, sheet_name=sheet_name)
    print(f"Emails sent: {sent}")
    print(f"Output: {Path(output_path).resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create Gmail drafts and send approved drafts."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    draft_parser = sub.add_parser(
        "drafts", help="Create Gmail drafts for generated emails."
    )
    draft_parser.add_argument("input")
    draft_parser.add_argument("output")
    draft_parser.add_argument("--sheet", default="Qualified Leads")

    send_parser = sub.add_parser(
        "send", help="Send only rows explicitly marked Approved."
    )
    send_parser.add_argument("input")
    send_parser.add_argument("output")
    send_parser.add_argument("--sheet", default="Qualified Leads")
    send_parser.add_argument("--confirm", action="store_true")

    args = parser.parse_args()
    if args.command == "drafts":
        create_drafts(args.input, args.output, args.sheet)
    else:
        send_approved(args.input, args.output, args.sheet, args.confirm)
