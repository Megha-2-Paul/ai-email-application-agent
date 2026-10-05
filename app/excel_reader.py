from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "Company",
    "Current Role",
    "Job Description / Requirements",
    "Public Email",
}


def load_job_sheet(path: str | Path, sheet_name: str = "Qualified Leads") -> pd.DataFrame:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {source}")

    if source.suffix.lower() == ".csv":
        df = pd.read_csv(source)
    elif source.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(source, sheet_name=sheet_name)
    else:
        raise ValueError("Supported input formats are .csv, .xlsx and .xls")

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
    return df


def rows_with_email(df: pd.DataFrame) -> pd.DataFrame:
    emails = df["Public Email"].fillna("").astype(str).str.strip()
    return df.loc[emails.ne("")].copy()


def add_output_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in (
        "Generated Subject",
        "Generated Email",
        "Generation Status",
        "Generation Error",
    ):
        if column not in result.columns:
            result[column] = ""
    return result


def write_output(
    input_path: str | Path,
    output_path: str | Path,
    generated_df: pd.DataFrame,
    sheet_name: str = "Qualified Leads",
) -> None:
    input_path = Path(input_path)
    output_path = Path(output_path)

    if input_path.suffix.lower() == ".csv":
        generated_df.to_csv(output_path, index=False)
        return

    sheets = pd.read_excel(input_path, sheet_name=None)
    sheets[sheet_name] = generated_df
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for name, sheet in sheets.items():
            sheet.to_excel(writer, sheet_name=name, index=False)
