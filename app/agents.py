"""LangChain agent — generates README.md from repository data using Gemini."""

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from app.config import settings


# ---------------------------------------------------------------------------
# Style definitions
# ---------------------------------------------------------------------------
STYLES = {
    "minimal": {
        "name": "Minimal",
        "description": "Short and focused. Only essential sections: title, description, install, usage.",
        "instructions": """
## Style: MINIMAL
- Keep it SHORT — aim for under 80 lines.
- Only include: Title, one-line Description, Quick Install, Basic Usage, License.
- No badges, no project structure tree, no contributing section.
- Prefer bullet points over paragraphs.
- Skip acknowledgments and extras.
""",
    },
    "detailed": {
        "name": "Detailed",
        "description": "Comprehensive and professional. All standard sections included.",
        "instructions": """
## Style: DETAILED
- Include ALL standard sections:
  1. Title & Badges (shields.io)
  2. Description (compelling, 2–3 sentences)
  3. Features (bullet list)
  4. Tech Stack
  5. Getting Started (prerequisites + installation)
  6. Usage (with code examples)
  7. Project Structure (directory tree)
  8. Contributing guidelines
  9. License
  10. Acknowledgments (if applicable)
- Be thorough but concise in each section.
""",
    },
    "awesome": {
        "name": "Awesome",
        "description": "Eye-catching with emojis, banners, and visual flair. Inspired by awesome-readme.",
        "instructions": """
## Style: AWESOME (Eye-catching)
- Use emojis liberally in headers and bullets (🚀 ✨ 📦 🛠️ 📖 🤝 📄 etc.)
- Start with a centered banner section: centered H1, tagline, and badge row.
- Include a Table of Contents with anchor links.
- Use HTML where helpful (centered text, badge rows, collapsible sections).
- Add a "Screenshots" or "Demo" section placeholder.
- Include ALL sections from the "detailed" style PLUS:
  - Table of Contents
  - Demo/Screenshots section
  - Roadmap section (infer from open issues/TODOs)
  - Show some personality and energy in the writing.
- Make it look like a top GitHub trending project README.
""",
    },
}


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are an expert technical writer who creates professional, comprehensive \
README.md files for open-source projects.

You will be given structured data about a GitHub repository (metadata, \
languages, file tree, config files, and an existing README if available). \
Use ALL of this information to generate a polished, production-quality README.

{style_instructions}

{custom_instructions_block}

## Rules
- Be concise but thorough.
- Write in **Markdown** format.
- Use code blocks for commands.
- Do NOT invent features or dependencies that are not evident in the data.
- If an existing README is provided, improve upon it rather than starting from scratch.
- Output ONLY the README markdown — no preamble, no explanation.
"""

USER_TEMPLATE = """\
Here is the repository data:

### Metadata
```json
{metadata}
```

### Languages
```json
{languages}
```

### File Tree
```
{file_tree}
```

### Important Config Files
{important_files}

### Existing README
{existing_readme}

---
Generate a professional README.md for this repository.
"""

# ---------------------------------------------------------------------------
# Analyze prompt
# ---------------------------------------------------------------------------
ANALYZE_SYSTEM_PROMPT = """\
You are a README quality analyst. You evaluate GitHub repository README files \
and provide a structured quality assessment.

Analyze the given README against these criteria:
1. **Clarity** (0-20): Is the project description clear and compelling?
2. **Completeness** (0-20): Are all important sections present?
3. **Installation** (0-20): Are setup/install instructions clear and complete?
4. **Usage** (0-20): Are usage examples provided and helpful?
5. **Presentation** (0-20): Good formatting, badges, structure?

Expected sections: Title, Description, Installation, Usage, Features, \
Contributing, License, Tech Stack, Project Structure.

You MUST respond with valid JSON only — no markdown, no code fences, no explanation. \
Use this exact structure:
{{"score": <0-100>, "summary": "<brief analysis>", "strengths": ["<strength1>", ...], "improvements": ["<suggestion1>", ...], "missing_sections": ["<section1>", ...]}}
"""

ANALYZE_USER_TEMPLATE = """\
Repository: {repo_name}

README content:
```
{existing_readme}
```

Repository metadata:
```json
{metadata}
```

Analyze this README and return JSON.
"""


def _format_important_files(files: dict) -> str:
    """Format the important files dict into a readable string for the prompt."""
    if not files:
        return "_No config files found._"

    sections = []
    for path, content in files.items():
        sections.append(f"**{path}**\n```\n{content}\n```")
    return "\n\n".join(sections)


def _get_llm():
    """Create the Gemini LLM instance."""
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.4,
        max_output_tokens=8192,
    )


def build_chain(style: str = "detailed", custom_instructions: str = ""):
    """Build the LangChain chain for README generation using Gemini."""
    llm = _get_llm()

    # Get style instructions
    style_config = STYLES.get(style, STYLES["detailed"])
    style_instructions = style_config["instructions"]

    # Build custom instructions block
    custom_instructions_block = ""
    if custom_instructions.strip():
        custom_instructions_block = f"""
## Custom Instructions from User
Follow these additional instructions carefully:
{custom_instructions}
"""

    system_prompt = SYSTEM_PROMPT.format(
        style_instructions=style_instructions,
        custom_instructions_block=custom_instructions_block,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", USER_TEMPLATE),
    ])

    chain = prompt | llm | StrOutputParser()
    return chain


def generate_readme(repo_data: dict, style: str = "detailed", custom_instructions: str = "") -> str:
    """Generate a README.md from the fetched repository data.

    Args:
        repo_data: dict returned by tools.fetch_repo_data()
        style: README style — "minimal", "detailed", or "awesome"
        custom_instructions: Optional extra instructions from the user

    Returns:
        Generated README content as a Markdown string.
    """
    chain = build_chain(style=style, custom_instructions=custom_instructions)

    result = chain.invoke({
        "metadata": json.dumps(repo_data["metadata"], indent=2),
        "languages": json.dumps(repo_data["languages"], indent=2),
        "file_tree": repo_data["file_tree"] or "No file tree available",
        "important_files": _format_important_files(repo_data.get("important_files", {})),
        "existing_readme": repo_data.get("existing_readme") or "_No existing README found._",
    })

    return result.strip()


def analyze_readme(repo_data: dict) -> dict:
    """Analyze an existing README and return a quality assessment.

    Args:
        repo_data: dict returned by tools.fetch_repo_data()

    Returns:
        dict with score, summary, strengths, improvements, missing_sections
    """
    llm = _get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", ANALYZE_SYSTEM_PROMPT),
        ("human", ANALYZE_USER_TEMPLATE),
    ])

    chain = prompt | llm | JsonOutputParser()

    result = chain.invoke({
        "repo_name": repo_data["metadata"]["full_name"],
        "existing_readme": repo_data.get("existing_readme") or "_No README found._",
        "metadata": json.dumps(repo_data["metadata"], indent=2),
    })

    return result
