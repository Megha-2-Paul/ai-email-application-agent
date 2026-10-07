import pandas as pd

from app.excel_reader import load_job_sheets


def test_load_job_sheets_combines_and_deduplicates(tmp_path):
    first = tmp_path / "first.xlsx"
    second = tmp_path / "second.xlsx"

    base = {
        "Company": ["Example", "Another"],
        "Current Role": ["Data Analyst", "Python Developer"],
        "Job Description / Requirements": ["SQL", "FastAPI"],
        "Public Email": ["one@example.com", "two@example.com"],
        "Job / Apply URL": ["https://example.com/1", "https://example.com/2"],
    }
    second_rows = {
        "Company": ["Example", "Third"],
        "Current Role": ["Data Analyst", "Data Scientist"],
        "Job Description / Requirements": ["SQL", "Python and SQL"],
        "Public Email": ["new@example.com", "three@example.com"],
        "Job / Apply URL": ["https://example.com/1", "https://example.com/3"],
    }

    pd.DataFrame(base).to_excel(first, index=False, sheet_name="Qualified Leads")
    pd.DataFrame(second_rows).to_excel(
        second, index=False, sheet_name="Qualified Leads"
    )

    result = load_job_sheets([first, second])

    assert len(result) == 3
    assert set(result["Source File"]) == {"first.xlsx", "second.xlsx"}
    assert "new@example.com" not in set(result["Public Email"])


def test_load_job_sheets_deduplicates_company_legal_suffix_variants(tmp_path):
    first = tmp_path / "first.xlsx"
    second = tmp_path / "second.xlsx"

    columns = {
        "Company": ["Madhu Jayanti International"],
        "Current Role": ["Python Developer - AI & Automation"],
        "Job Description / Requirements": ["Python and AI"],
        "Public Email": ["mandakranta.amahpatra@jaytea.com"],
        "Job / Apply URL": ["https://example.com/madhu"],
    }
    duplicate = {
        "Company": ["Madhu Jayanti International Pvt. Ltd."],
        "Current Role": ["Python Developer - AI & Automation"],
        "Job Description / Requirements": ["Python and AI"],
        "Public Email": ["mandakranta.amahpatra@jaytea.com"],
        "Job / Apply URL": ["https://example.com/madhu"],
    }

    pd.DataFrame(columns).to_excel(first, index=False, sheet_name="Qualified Leads")
    pd.DataFrame(duplicate).to_excel(
        second, index=False, sheet_name="Qualified Leads"
    )

    result = load_job_sheets([first, second])
    assert len(result) == 1
