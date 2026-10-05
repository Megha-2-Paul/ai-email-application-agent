import pandas as pd
import pytest

from gmail_workflow import send_approved


def test_send_requires_confirmation(tmp_path):
    path = tmp_path / "input.csv"
    pd.DataFrame([
        {
            "Company": "Example",
            "Current Role": "Python Developer",
            "Job Description / Requirements": "Python",
            "Public Email": "person@example.com",
            "Gmail Draft ID": "draft-1",
            "Gmail Approval": "Approved",
        }
    ]).to_csv(path, index=False)

    with pytest.raises(ValueError, match="--confirm"):
        send_approved(str(path), str(tmp_path / "output.csv"), confirm=False)
