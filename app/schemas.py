# Purpose: define the structure of a candidate's 
# résumé and validate incoming API data.
from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    role: str
    company: str
    dates: str = ""
    bullets: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    name: str
    technologies: list[str] = Field(default_factory=list)
    description: str
    bullets: list[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)


class TailorRequest(BaseModel):
    profile: CandidateProfile
    job_title: str = "Target Role"
    job_description: str = Field(min_length=20)


class TailorResponse(BaseModel):
    candidate_name: str
    job_title: str
    match_percentage: int
    matched_skills: list[str]
    missing_skills: list[str]
    profile: CandidateProfile
    notes: list[str]