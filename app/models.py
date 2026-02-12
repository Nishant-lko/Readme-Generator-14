"""Pydantic models for API request / response validation."""

from typing import Optional
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request body for the /api/generate endpoint."""

    repo_url: str = Field(
        ...,
        description="Full GitHub repository URL, e.g. https://github.com/owner/repo",
        examples=["https://github.com/tiangolo/fastapi"],
    )
    style: str = Field(
        default="detailed",
        description="README style: minimal, detailed, or awesome",
    )
    custom_instructions: str = Field(
        default="",
        description="Optional custom instructions for README generation",
    )
    github_token: Optional[str] = Field(
        default=None,
        description="Optional GitHub token for private repo access",
    )


class GenerateResponse(BaseModel):
    """Response body returned after README generation."""

    readme_content: str = Field(..., description="Generated README in Markdown format")
    repo_name: str = Field(..., description="Repository full name (owner/repo)")
    generation_time: float = Field(..., description="Time taken to generate in seconds")


class AnalyzeRequest(BaseModel):
    """Request body for the /api/analyze endpoint."""

    repo_url: str = Field(
        ...,
        description="Full GitHub repository URL",
    )
    github_token: Optional[str] = Field(
        default=None,
        description="Optional GitHub token for private repo access",
    )


class AnalyzeResponse(BaseModel):
    """Response body for README analysis."""

    score: int = Field(..., description="README quality score out of 100")
    summary: str = Field(..., description="Brief summary of the analysis")
    strengths: list[str] = Field(default_factory=list, description="What the README does well")
    improvements: list[str] = Field(default_factory=list, description="Suggested improvements")
    missing_sections: list[str] = Field(default_factory=list, description="Missing recommended sections")
    repo_name: str = Field(..., description="Repository full name")


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(..., description="Human-readable error message")
