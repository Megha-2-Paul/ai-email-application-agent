import argparse
from pathlib import Path

from app.email_generator import EmailGenerator
from app.excel_reader import (
    add_output_columns,
    load_job_sheet,
    load_job_sheets,
    rows_with_email,
    write_combined_output,
    write_output,
)
from app.resume_selector import select_resume_type


def generate_emails(
    input_path: str,
    output_path: str,
    sheet_name: str = "Qualified Leads",
    additional_inputs: list[str] | None = None,
) -> None:
    source_paths = [input_path, *(additional_inputs or [])]
    if len(source_paths) == 1:
        jobs = load_job_sheet(input_path, sheet_name=sheet_name)
    else:
        jobs = load_job_sheets(source_paths, sheet_name=sheet_name)

    result = add_output_columns(jobs)
    eligible = rows_with_email(result)
    generator = EmailGenerator()

    generated = 0
    skipped = len(result) - len(eligible)

    for index, row in eligible.iterrows():
        try:
            subject, body = generator.generate(row.to_dict())
            result.at[index, "Generated Subject"] = subject
            result.at[index, "Generated Email"] = body
            result.at[index, "Generation Status"] = "Generated"
            result.at[index, "Generation Error"] = ""
            result.at[index, "Resume Used"] = select_resume_type(row.to_dict())
            generated += 1
        except Exception as exc:
            result.at[index, "Generation Status"] = "Error"
            result.at[index, "Generation Error"] = str(exc)

    if len(source_paths) == 1:
        write_output(input_path, output_path, result, sheet_name=sheet_name)
    else:
        write_combined_output(output_path, result, source_paths)

    print(f"Rows loaded: {len(result)}")
    print(f"Emails generated: {generated}")
    print(f"Rows skipped (no public email): {skipped}")
    print(f"Output: {Path(output_path).resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate job application emails with Groq."
    )
    parser.add_argument("input", help="Primary CSV/XLSX input file")
    parser.add_argument("output", help="Path for generated CSV/XLSX output file")
    parser.add_argument(
        "--additional-input",
        action="append",
        default=[],
        help="Additional job file. Repeat this option to combine multiple files.",
    )
    parser.add_argument("--sheet", default="Qualified Leads")
    args = parser.parse_args()
    generate_emails(
        args.input,
        args.output,
        sheet_name=args.sheet,
        additional_inputs=args.additional_input,
    )
