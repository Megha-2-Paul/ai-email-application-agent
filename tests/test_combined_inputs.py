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
    duplicate = {
        "Company": ["Example"],
        "Current Role": ["Data Analyst"],
        "Job Description / Requirements": ["SQL"],
        "Public Email": ["new@example.com"],
        "Job / Apply URL": ["https://example.com/1"],
    }

    pd.DataFrame(base).to_excel(first, index=False, sheet_name="Qualified Leads")
    pd.DataFrame(duplicate).to_excel(second, index=False, sheet_name="Qualified Leads")

    result = load_job_sheets([first, second])

    assert len(result) == 2
    assert set(result["Source File"]) == {"first.xlsx", "second.xlsx"}
