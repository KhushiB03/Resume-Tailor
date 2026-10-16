# Purpose: identify skills mentioned in the job description, compare them with the candidate's information, and rank existing projects by relevance.
import re
#re is a built-in Python module used for Regular Expressions

from app.schemas import TailorRequest, TailorResponse, CandidateProfile


COMMON_SKILLS = {
    "python", "java", "javascript", "typescript", "sql", "postgresql",
    "mysql", "mongodb", "fastapi", "flask", "django", "node.js",
    "express", "react", "scikit-learn", "pandas", "numpy", "pytorch",
    "tensorflow", "machine learning", "deep learning", "nlp",
    "generative ai", "llm", "rag", "embeddings", "docker",
    "kubernetes", "aws", "azure", "google cloud", "git",
    "github actions", "mlflow", "rest api", "api development",
    "data analysis", "data visualization", "communication",
    "problem solving", "testing", "ci/cd",
}


def normalize(text: str) -> str:
    """Normalize text to simplify keyword matching."""
    return re.sub(r"[^a-z0-9+#./ -]", " ", text.lower())
# re.sub(pattern, replacement, text)
# pattern — what you want to find.
# replacement — what you want to replace it with.
# text — the original text.


def contains_skill(text: str, skill: str) -> bool:
    """Match a skill as a phrase rather than part of another word."""
    pattern = (
        rf"(?<![a-z0-9]){re.escape(skill.lower())}"
        rf"(?![a-z0-9])"
    )
    return bool(re.search(pattern, text))


def extract_job_skills(job_description: str) -> list[str]:
    """Find recognized skills in a job description."""
    text = normalize(job_description)

    return [
        skill
        for skill in sorted(COMMON_SKILLS, key=len, reverse=True)
        if contains_skill(text, skill)
    ]


def profile_text(profile: CandidateProfile) -> str:
    """Combine profile fields into searchable text."""
    parts = [
        profile.summary,
        *profile.skills,
        *profile.education,
    ]

    for experience in profile.experience:
        parts.extend([
            experience.role,
            experience.company,
            experience.dates,
            *experience.bullets,
        ])

    for project in profile.projects:
        parts.extend([
            project.name,
            project.description,
            *project.technologies,
            *project.bullets,
        ])

    return normalize(" ".join(parts))


def score_text_against_skills(
    text: str,
    job_skills: list[str],
) -> int:
    """Count how many target skills occur in a piece of text."""
    return sum(
        1 for skill in job_skills
        if contains_skill(text, skill)
    )


def tailor_profile(request: TailorRequest) -> TailorResponse:
    profile = request.profile

    job_skills = extract_job_skills(
        request.job_description
    )

    all_text = profile_text(profile)

    matched_skills = [
        skill for skill in job_skills
        if contains_skill(all_text, skill)
    ]

    missing_skills = [
        skill for skill in job_skills
        if skill not in matched_skills
    ]

    match_percentage = (
        round(100 * len(matched_skills) / len(job_skills))
        if job_skills
        else 0
    )

    # Put recognized, relevant skills first.
    # Do not add skills that the candidate did not provide.
    target_order = {
        skill: index
        for index, skill in enumerate(job_skills)
    }

    ordered_skills = sorted(
        profile.skills,
        key=lambda skill: (
            skill.lower() not in target_order,
            target_order.get(skill.lower(), 9999),
        ),
    )

    # Rank projects using the skills found in their own descriptions.
    def project_relevance(project):
        project_text = normalize(" ".join([
            project.name,
            project.description,
            *project.technologies,
            *project.bullets,
        ]))

        return score_text_against_skills(
            project_text,
            job_skills,
        )

    ordered_projects = sorted(
        profile.projects,
        key=project_relevance,
        reverse=True,
    )

    tailored_profile = profile.model_copy(
        update={
            "skills": ordered_skills,
            "projects": ordered_projects,
        }
    )

    notes = [
        "This version uses keyword matching, not a trained hiring model.",
        "The match score measures detected skill overlap only.",
        "Review all content before using the generated résumé.",
    ]

    if not job_skills:
        notes.append(
            "No recognized skills were detected. "
            "Expand the skill vocabulary or use a more specific job description."
        )

    return TailorResponse(
        candidate_name=profile.name,
        job_title=request.job_title,
        match_percentage=match_percentage,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        profile=tailored_profile,
        notes=notes,
    )