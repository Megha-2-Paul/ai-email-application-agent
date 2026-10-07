# AI Email Application Agent

AI-assisted job application email generator with Groq personalization and a human-controlled Gmail workflow.

## Current workflow

1. One or more Excel/CSV job files -> normalize/deduplicate -> Groq -> personalized application emails
2. Generated emails include Megha Paul's contact signature and LinkedIn profile
3. Each generated row is classified for the most suitable local resume:
   - Data Analyst Resume
   - Python Developer Resume
4. Gmail OAuth -> create Gmail drafts
5. Review drafts in Gmail
6. Mark selected spreadsheet rows as `Approved`
7. Run the explicit send command with `--confirm`
8. Gmail API sends only approved drafts

No job scraping, background application tracking, or unattended sending is included.

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

Multiple job files can be combined. Duplicate rows are removed using normalized company, role, and application URL values, and the originating filename is retained in `Source File`.

## Generated columns

The generator adds:

- Generated Subject
- Generated Email
- Generation Status
- Generation Error
- Resume Used

The Gmail workflow adds:

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
6. Keep `credentials.json`, `token.json`, resumes, and personal job-list spreadsheets out of Git.

Never commit `.env`, OAuth credentials, tokens, resumes, or personal job-list spreadsheets.

## Generate from one job file

```bash
python main.py jobs.xlsx generated_jobs.xlsx
```

## Generate from multiple job files

Keep the primary input first and repeat `--additional-input` for each additional workbook:

```bash
python main.py jobs.xlsx combined_generated_jobs.xlsx --additional-input latest_jobs.xlsx
```

The combined output contains a `Qualified Leads` sheet plus a `Source Files` sheet.

Inspect the generated workbook before moving to Gmail.

## Candidate signature

Generated email bodies end with:

- Megha Paul
- Associate Data Analyst
- +91 6289771661
- meghapaul0202@gmail.com
- LinkedIn profile

Contact information is centralized in `app/config.py`.

## Resume selection

Resume selection is deterministic and based on the job role, role family, requirements, and notes.

Analytics-oriented roles such as Data Analyst, Business Intelligence, MIS, Data Science, and Power BI roles use the Data Analyst resume.

Python/backend/AI-oriented roles such as Python Developer, Backend, FastAPI, AI Engineer, ML Engineer, GenAI, RAG, and LLM roles use the Python Developer resume.

Resume PDFs remain local and are ignored by Git.

## Gmail drafts

```bash
python gmail_workflow.py drafts generated_jobs.xlsx gmail_drafts.xlsx
```

The first run opens the Google OAuth consent flow. Drafts are created in your Gmail account but are not sent.

The workflow validates recipient addresses and skips duplicate recipient+subject pairs within the same batch. Existing rows with a Gmail Draft ID are not recreated.

Open Gmail, review the drafts, then set `Gmail Approval` to `Approved` only for emails you want to send.

## Send approved drafts

```bash
python gmail_workflow.py send gmail_drafts.xlsx sent_jobs.xlsx --confirm
```

The `--confirm` flag is mandatory. The command sends only rows whose `Gmail Approval` is exactly `Approved`, have a Gmail Draft ID, and have not already been marked sent.

Already-sent rows are skipped, so rerunning the command does not resend rows that were successfully recorded as sent.

## Validation and error handling

- Public email cells can contain multiple addresses separated by punctuation; recipient extraction deduplicates them.
- Invalid or missing recipients are skipped.
- Missing generated subject/body is skipped.
- Duplicate recipient+subject pairs in the same draft batch are skipped.
- Gmail draft/send failures are recorded in `Gmail Send Status` and processing continues for the remaining rows.
- Unit tests mock Gmail, so automated tests never send real email.

## Testing

Run the full automated test suite with:

```bash
pytest -q
```

Tests cover email parsing and signatures, role-based resume selection, combined input deduplication, Gmail attachment message construction, approval-gated sending, duplicate/invalid-row handling, idempotent send behavior, and Gmail error recording.

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
- V5: Multiple job-file ingestion, candidate contact signature, and deterministic resume selection
- Future: job-fit scoring, duplicate detection, reply handling, and interview preparation
