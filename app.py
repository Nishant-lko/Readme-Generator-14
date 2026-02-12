"""FastAPI application — serves the API and static frontend."""

import time
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.models import GenerateRequest, GenerateResponse, AnalyzeRequest, AnalyzeResponse
from app.tools import fetch_repo_data
from app.agents import generate_readme, analyze_readme, STYLES

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI README Generator",
    description="Generate professional README.md files using LangChain + GitHub API",
    version="2.0.0",
)

# CORS — allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "AI README Generator"}


@app.get("/api/styles")
async def get_styles():
    """Return available README styles."""
    return {
        key: {"name": val["name"], "description": val["description"]}
        for key, val in STYLES.items()
    }


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """Generate a README.md for the given GitHub repository URL."""
    logger.info(f"Generating README for: {request.repo_url} (style={request.style})")
    start_time = time.time()

    try:
        # Determine which GitHub token to use
        from app.config import settings
        token = request.github_token or settings.github_token

        # Step 1 — Fetch repository data via GitHub API
        logger.info("Fetching repository data...")
        repo_data = fetch_repo_data(request.repo_url, github_token=token)
        logger.info(f"Fetched data for: {repo_data['metadata']['full_name']}")

        # Step 2 — Generate README via LangChain
        logger.info("Generating README with LangChain...")
        readme_content = generate_readme(
            repo_data,
            style=request.style,
            custom_instructions=request.custom_instructions,
        )

        elapsed = round(time.time() - start_time, 2)
        logger.info(f"README generated in {elapsed}s")

        return GenerateResponse(
            readme_content=readme_content,
            repo_name=repo_data["metadata"]["full_name"],
            generation_time=elapsed,
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate README: {str(e)}")


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """Analyze an existing README and give a quality score."""
    logger.info(f"Analyzing README for: {request.repo_url}")

    try:
        from app.config import settings
        token = request.github_token or settings.github_token

        # Fetch repository data
        repo_data = fetch_repo_data(request.repo_url, github_token=token)
        repo_name = repo_data["metadata"]["full_name"]

        if not repo_data.get("existing_readme"):
            raise ValueError(f"No existing README found in {repo_name}. Nothing to analyze.")

        # Analyze via LangChain
        logger.info("Analyzing README with LangChain...")
        analysis = analyze_readme(repo_data)

        return AnalyzeResponse(
            score=analysis.get("score", 0),
            summary=analysis.get("summary", ""),
            strengths=analysis.get("strengths", []),
            improvements=analysis.get("improvements", []),
            missing_sections=analysis.get("missing_sections", []),
            repo_name=repo_name,
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze README: {str(e)}")


# ---------------------------------------------------------------------------
# Serve static frontend
# ---------------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the main HTML page."""
    return FileResponse("static/index.html")


# ---------------------------------------------------------------------------
# Run directly: python app.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
