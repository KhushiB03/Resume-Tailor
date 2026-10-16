from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)

from app.schemas import TailorResponse


def create_resume_pdf(result: TailorResponse) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"{result.candidate_name} - Tailored Resume",
        author="AI Resume Tailor",
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CandidateName",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#17324D"),
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="ContactLine",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=8.5,
        leading=11,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#17324D"),
        spaceBefore=8,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="SmallBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        spaceAfter=3,
    ))

    story = []
    profile = result.profile

    # Candidate name and contact information
    story.append(
        Paragraph(
            escape(profile.name),
            styles["CandidateName"],
        )
    )

    contact = " | ".join(
        value
        for value in [
            profile.email,
            profile.phone,
            profile.location,
        ]
        if value
    )

    if contact:
        story.append(
            Paragraph(
                escape(contact),
                styles["ContactLine"],
            )
        )

    story.append(
        HRFlowable(
            width="100%",
            thickness=0.8,
            color=colors.HexColor("#A8B8C8"),
        )
    )

    story.append(Spacer(1, 5))

    def add_section(title):
        story.append(
            Paragraph(
                escape(title.upper()),
                styles["SectionHeading"],
            )
        )

        story.append(
            HRFlowable(
                width="100%",
                thickness=0.4,
                color=colors.HexColor("#D5DDE5"),
            )
        )

        story.append(Spacer(1, 4))

    def add_bullet(text):
        story.append(
            Paragraph(
                "&#8226; " + escape(text),
                styles["SmallBody"],
            )
        )

    # Summary
    if profile.summary:
        add_section("Professional Summary")
        story.append(
            Paragraph(
                escape(profile.summary),
                styles["SmallBody"],
            )
        )

    # Skills
    if profile.skills:
        add_section("Skills")
        story.append(
            Paragraph(
                escape(" • ".join(profile.skills)),
                styles["SmallBody"],
            )
        )

    # Projects
    if profile.projects:
        add_section("Projects")

        for project in profile.projects:
            story.append(
                Paragraph(
                    f"<b>{escape(project.name)}</b>",
                    styles["SmallBody"],
                )
            )

            if project.technologies:
                story.append(
                    Paragraph(
                        "<i>Technologies: "
                        + escape(", ".join(project.technologies))
                        + "</i>",
                        styles["SmallBody"],
                    )
                )

            story.append(
                Paragraph(
                    escape(project.description),
                    styles["SmallBody"],
                )
            )

            for bullet in project.bullets:
                add_bullet(bullet)

    # Experience
    if profile.experience:
        add_section("Experience")

        for experience in profile.experience:
            heading = (
                f"<b>{escape(experience.role)}</b> — "
                f"{escape(experience.company)}"
            )

            if experience.dates:
                heading += f" ({escape(experience.dates)})"

            story.append(
                Paragraph(
                    heading,
                    styles["SmallBody"],
                )
            )

            for bullet in experience.bullets:
                add_bullet(bullet)

    # Education
    if profile.education:
        add_section("Education")

        for education_item in profile.education:
            add_bullet(education_item)

    doc.build(story)

    return buffer.getvalue()