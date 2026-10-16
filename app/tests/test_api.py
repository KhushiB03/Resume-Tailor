
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Load the example request supplied with the project.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILE = PROJECT_ROOT / "sample_request.json"

with SAMPLE_FILE.open("r", encoding="utf-8") as file:
    SAMPLE_REQUEST = json.load(file)


def test_home_endpoint():
    """The home endpoint should respond successfully."""
    response = client.get("/")

    assert response.status_code == 200


def test_tailor_returns_matching_results():
    """The tailoring endpoint should return the expected fields."""
    response = client.post("/tailor", json=SAMPLE_REQUEST)

    assert response.status_code == 200

    data = response.json()

    assert "match_percentage" in data
    assert "matched_skills" in data
    assert "missing_skills" in data
    assert "profile" in data

    assert isinstance(data["match_percentage"], (int, float))
    assert 0 <= data["match_percentage"] <= 100
    assert isinstance(data["matched_skills"], list)
    assert isinstance(data["missing_skills"], list)


def test_tailor_pdf_returns_pdf():
    """The PDF endpoint should return a PDF file."""
    response = client.post("/tailor/pdf", json=SAMPLE_REQUEST)

    assert response.status_code == 200
    assert "application/pdf" in response.headers["content-type"]
    assert response.content.startswith(b"%PDF")


def test_tailor_rejects_invalid_request():
    """A request missing required fields should be rejected."""
    response = client.post("/tailor", json={})

    assert response.status_code == 422
