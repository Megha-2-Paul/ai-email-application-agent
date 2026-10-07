from app.resume_selector import (
    DATA_ANALYST_RESUME,
    PYTHON_DEVELOPER_RESUME,
    select_resume_type,
)


def test_selects_data_analyst_resume_for_analytics_role():
    row = {
        "Current Role": "Data Analyst",
        "Role Family": "Data Analytics / BI / Python",
        "Job Description / Requirements": "SQL, Power BI, dashboards and KPI analysis",
    }
    assert select_resume_type(row) == DATA_ANALYST_RESUME


def test_selects_python_resume_for_backend_ai_role():
    row = {
        "Current Role": "Python Backend Developer",
        "Role Family": "Backend / Python / AI",
        "Job Description / Requirements": "FastAPI, REST APIs, RAG and LLM applications",
    }
    assert select_resume_type(row) == PYTHON_DEVELOPER_RESUME


def test_python_role_wins_when_requirements_contain_data_terms():
    row = {
        "Current Role": "Python Developer - AI & Automation",
        "Role Family": "Python / AI / Automation",
        "Job Description / Requirements": (
            "Python, SQL, data analysis, dashboards, automation and APIs"
        ),
    }
    assert select_resume_type(row) == PYTHON_DEVELOPER_RESUME


def test_ai_role_defaults_to_python_resume_when_scores_tie():
    row = {
        "Current Role": "AI Engineer",
        "Role Family": "AI / ML / Python",
        "Job Description / Requirements": "Python and machine learning",
    }
    assert select_resume_type(row) == PYTHON_DEVELOPER_RESUME
