# AI Email Application Agent

AI-assisted job application email generator.

## V1 scope

- Read job leads from CSV or Excel.
- Use the Groq API to generate personalized application emails.
- Preserve the source workbook structure and append generated email fields.
- Skip rows without a usable public email.
- Keep API keys and local job data out of Git.
- Gmail OAuth and sending will be added in the next milestone.

## Input

The agent is designed around the `Qualified Leads` sheet in the job-research workbook. Expected columns include:

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

## Output

The generated workbook keeps the original columns and adds:

- Generated Subject
- Generated Email
- Generation Status
- Generation Error

## Local setup

1. Create a Python virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Add your Groq API key locally.
5. Run the generator against a copy of your job-research workbook.

Never commit `.env`, OAuth credentials, tokens, or personal job-list spreadsheets.

## Roadmap

1. Excel/CSV -> Groq -> generated email workbook
2. Gmail OAuth -> Gmail drafts
3. Approved draft -> Gmail send
4. Optional batch approval and sending controls
