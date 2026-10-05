import pandas as pd
import pytest

from app.excel_reader import add_output_columns, load_job_sheet, rows_with_email


def test_required_columns_are_validated(tmp_path):
    path = tmp_path / "jobs.csv"
    pd.DataFrame({"Company": ["Example"]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="Missing required columns"):
        load_job_sheet(path)


def test_rows_with_email_filters_empty_addresses():
    df = pd.DataFrame({
        "Company": ["A", "B"],
        "Current Role": ["Python Developer", "Data Analyst"],
        "Job Description / Requirements": ["Python", "SQL"],
        "Public Email": ["hr@example.com", ""],
    })
    result = rows_with_email(df)
    assert len(result) == 1
    assert result.iloc[0]["Company"] == "A"


def test_output_columns_are_added():
    df = pd.DataFrame({
        "Company": ["A"],
        "Current Role": ["Python Developer"],
        "Job Description / Requirements": ["Python"],
        "Public Email": ["hr@example.com"],
    })
    result = add_output_columns(df)
    assert "Generated Subject" in result.columns
    assert "Generated Email" in result.columns
    assert "Generation Status" in result.columns
    assert "Generation Error" in result.columns
