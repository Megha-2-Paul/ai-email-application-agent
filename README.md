# AI Email Application Agent

AI-assisted job application email generator with Groq personalization and a human-controlled Gmail workflow.

## Current workflow

1. Excel/CSV -> Groq -> personalized application emails
2. Gmail OAuth -> create Gmail drafts
3. Review drafts in Gmail
4. Mark selected spreadsheet rows as `Approved`
5. Run the explicit send command with `--confirm`
6. Gmail API sends only approved drafts

No job scraping, automatic sending, or background application tracking is included.

## Input

The agent is designed around the `Qualified Leads` sheet. Expected columns include:

- Company
- Current Role
- Role Family
- Work Location
- Work Mode
- Experience
- Employment Type
- Payroll / Employer Status
- Job Description / Requirements
- Recruiter / Contact
- Public Email
- Job / Apply URL
- Priority
- Notes
- Action

## Generated columns

V1 adds:

- Generated Subject
- Generated Email
- Generation Status
- Generation Error

V2/V3 adds:

- Gmail Draft ID
- Gmail Draft Status
- Gmail Approval
- Gmail Send Status

## Local setup

1. Create a Python virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and add your Groq API key.
4. Configure a Google Cloud OAuth Desktop App for the Gmail API.
5. Download the OAuth client JSON and save it locally as `credentials.json`.
6. Keep `credentials.json` and the generated `token.json` out of Git.

Never commit `.env`, OAuth credentials, tokens, or personal job-list spreadsheets.

## V1: Generate emails

```bash
python main.py data/jobs.xlsx data/generated_jobs.xlsx
```

Inspect the generated workbook before moving to Gmail.

## V2: Create Gmail drafts

```bash
python gmail_workflow.py drafts data/generated_jobs.xlsx data/gmail_drafts.xlsx
```

The first run opens the Google OAuth consent flow. Drafts are created in your Gmail account but are not sent.

The workflow validates recipient addresses and skips duplicate recipient+subject pairs within the same batch. Existing rows with a Gmail Draft ID are not recreated.

Open Gmail, review the drafts, then set `Gmail Approval` to `Approved` only for emails you want to send.

## V3: Send approved drafts

```bash
python gmail_workflow.py send data/gmail_drafts.xlsx data/sent_jobs.xlsx --confirm
```

The `--confirm` flag is mandatory. The command sends only rows whose `Gmail Approval` is exactly `Approved`, have a Gmail Draft ID, and have not already been marked sent.

Already-sent rows are skipped, so rerunning the command does not resend rows that were successfully recorded as sent.

## Validation and error handling

- Invalid recipient addresses are marked `Invalid Email`.
- Missing generated subject/body/email is marked `Skipped`.
- Duplicate recipient+subject pairs in the same draft batch are marked `Duplicate Skipped`.
- Gmail draft/send failures are recorded in `Gmail Send Status` and processing continues for the remaining rows.
- Unit tests mock Gmail, so automated tests never send real email.

## Testing

Run the full automated test suite with:

```bash
pytest -q
```

These tests cover the approval gate, draft creation, duplicate/invalid-row handling, approved-only sending, idempotent send behavior, and Gmail error recording.

## Safety design

- OAuth credentials and tokens stay local.
- Draft creation never sends mail.
- Sending requires both a spreadsheet approval value and an explicit `--confirm` flag.
- Already-sent rows are skipped.
- Rows without generated emails are skipped.
- Errors are written to the workbook instead of stopping the entire batch.

## Roadmap

- V1: Excel/CSV -> Groq -> generated email workbook
- V2: Gmail OAuth -> Gmail drafts
- V3: Human approval -> Gmail send
- V4: Validation, idempotency, error handling, and automated Gmail mocks
- Future: job-fit scoring, duplicate detection, reply handling, and interview preparation
