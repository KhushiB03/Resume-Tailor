from io import BytesIO

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from app.schemas import TailorRequest, TailorResponse
from app.services.matcher import tailor_profile
from app.services.pdf_generator import create_resume_pdf


app = FastAPI(
    title="AI Resume Tailor",
    description="A free, local-first résumé tailoring MVP.",
    version="0.1.0",
)


@app.get("/")
def home():
    return {
        "message": "AI Resume Tailor is running",
        "docs": "/docs",
        "next_step": "Use POST /tailor or POST /tailor/pdf",
    }


@app.post("/tailor", response_model=TailorResponse)
def tailor_resume(request: TailorRequest):
    """Match a candidate profile against a job description."""
    return tailor_profile(request)


@app.post("/tailor/pdf")
def download_tailored_pdf(request: TailorRequest):
    """Generate and return a tailored résumé PDF."""
    result = tailor_profile(request)
    pdf_bytes = create_resume_pdf(result)

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="tailored_resume.pdf"'
        },
    )