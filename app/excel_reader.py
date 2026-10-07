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


def load_job_sheets(paths: list[str | Path], sheet_name: str = "Qualified Leads") -> pd.DataFrame:
    frames = []
    for path in paths:
        frame = load_job_sheet(path, sheet_name=sheet_name).copy()
        frame["Source File"] = Path(path).name
        frames.append(frame)

    if not frames:
        raise ValueError("At least one input file is required.")

    result = pd.concat(frames, ignore_index=True, sort=False)

    def normalize(value):
        return " ".join(str(value or "").strip().lower().split())

    keys = result.apply(
        lambda row: (
            normalize(row.get("Company")),
            normalize(row.get("Current Role")),
            normalize(row.get("Job / Apply URL")),
        ),
        axis=1,
    )
    result["_dedupe_key"] = keys
    result = result.drop_duplicates(subset="_dedupe_key", keep="first").drop(
        columns="_dedupe_key"
    )
    return result.reset_index(drop=True)


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
        "Resume Used",
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


def write_combined_output(
    output_path: str | Path,
    generated_df: pd.DataFrame,
    source_paths: list[str | Path],
) -> None:
    output_path = Path(output_path)
    source_rows = pd.DataFrame(
        {
            "Source File": [Path(path).name for path in source_paths],
            "Source Path": [str(Path(path).resolve()) for path in source_paths],
        }
    )
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        generated_df.to_excel(writer, sheet_name="Qualified Leads", index=False)
        source_rows.to_excel(writer, sheet_name="Source Files", index=False)
