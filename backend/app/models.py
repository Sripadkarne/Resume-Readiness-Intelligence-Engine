"""Shared Pydantic models for agent interactions."""

from __future__ import annotations

from typing import Literal, Sequence
from pydantic import BaseModel, Field


class SkillCategory(BaseModel):
    name: str
    skills: list[str] = Field(default_factory=list)


class ExperienceEntry(BaseModel):
    position: str
    company: str | None = None
    bullets: list[str] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    name: str
    context: str | None = None
    bullets: list[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    degree: str
    institution: str
    courses: list[str] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    """Structured résumé representation returned by the parsing service."""

    raw_text: str
    skills: list[SkillCategory] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    other: list[str] = Field(default_factory=list)


class JobProfile(BaseModel):
    """Normalized job description metadata."""

    title: str | None = None
    company: str | None = None
    summary: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)


class SkillScore(BaseModel):
    skill: str
    score: float
    source: Literal["resume", "job"]


class SkillGap(BaseModel):
    skill: str
    resume_score: float | None = None
    target_score: float
    classification: Literal["missing", "needs_practice", "strong"]


class StudyResource(BaseModel):
    id: str
    title: str
    url: str
    resource_type: Literal["article", "video", "book", "course"]
    summary: str | None = None


class StudyPlanStep(BaseModel):
    skill: str
    objective: str
    resources: Sequence[StudyResource] = Field(default_factory=list)
    practice_ideas: list[str] = Field(default_factory=list)


class StudyPlan(BaseModel):
    learner_profile: ResumeProfile
    target_role: JobProfile
    steps: list[StudyPlanStep] = Field(default_factory=list)
    timeline_weeks: int | None = None
