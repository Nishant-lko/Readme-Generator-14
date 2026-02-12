"""GitHub API tools — fetch repository data without cloning."""

import re
import base64
from typing import Optional

from github import Github, GithubException, Auth


# Files worth reading for context about the project
IMPORTANT_FILES = [
    "setup.py",
    "setup.cfg",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".github/workflows",
    "LICENSE",
    "CONTRIBUTING.md",
]

# Maximum characters to read from any single file
MAX_FILE_CONTENT_LENGTH = 3000

# Maximum depth for the file tree
MAX_TREE_DEPTH = 3


def parse_repo_url(url: str) -> str:
    """Extract 'owner/repo' from a GitHub URL.

    Supports formats:
        - https://github.com/owner/repo
        - https://github.com/owner/repo.git
        - github.com/owner/repo
        - owner/repo
    """
    url = url.strip().rstrip("/")

    # Remove .git suffix
    if url.endswith(".git"):
        url = url[:-4]

    # Try full URL pattern
    match = re.match(r"(?:https?://)?github\.com/([^/]+/[^/]+)", url)
    if match:
        return match.group(1)

    # Try owner/repo pattern
    match = re.match(r"^([^/]+/[^/]+)$", url)
    if match:
        return match.group(1)

    raise ValueError(
        f"Invalid GitHub URL: '{url}'. "
        "Expected format: https://github.com/owner/repo"
    )


def _build_tree(repo, path: str = "", depth: int = 0) -> list[dict]:
    """Recursively build a file/folder tree up to MAX_TREE_DEPTH."""
    if depth >= MAX_TREE_DEPTH:
        return []

    try:
        contents = repo.get_contents(path)
    except GithubException:
        return []

    tree = []
    for item in contents:
        node = {
            "name": item.name,
            "type": "dir" if item.type == "dir" else "file",
            "path": item.path,
        }
        if item.type == "dir" and depth < MAX_TREE_DEPTH - 1:
            node["children"] = _build_tree(repo, item.path, depth + 1)
        tree.append(node)

    return tree


def _format_tree(tree: list[dict], prefix: str = "") -> str:
    """Format the tree structure as a readable string."""
    lines = []
    for i, node in enumerate(tree):
        is_last = i == len(tree) - 1
        connector = "└── " if is_last else "├── "
        icon = "📁 " if node["type"] == "dir" else "📄 "
        lines.append(f"{prefix}{connector}{icon}{node['name']}")

        if "children" in node:
            extension = "    " if is_last else "│   "
            lines.append(_format_tree(node["children"], prefix + extension))

    return "\n".join(lines)


def _read_file_content(repo, file_path: str) -> Optional[str]:
    """Read a single file's content from the repo (base64 decoded)."""
    try:
        content_file = repo.get_contents(file_path)
        if content_file.encoding == "base64" and content_file.content:
            decoded = base64.b64decode(content_file.content).decode("utf-8", errors="replace")
            return decoded[:MAX_FILE_CONTENT_LENGTH]
        return None
    except (GithubException, Exception):
        return None


def fetch_repo_data(repo_url: str, github_token: str = "") -> dict:
    """Fetch comprehensive repository data via the GitHub API.

    Returns a dict with:
        - metadata (name, description, stars, forks, language, topics, etc.)
        - languages (with byte counts)
        - file_tree (formatted string)
        - important_files (content of key config/build files)
        - existing_readme (content if one exists)
    """
    full_name = parse_repo_url(repo_url)

    # Authenticate if token provided
    if github_token:
        auth = Auth.Token(github_token)
        g = Github(auth=auth)
    else:
        g = Github()

    try:
        repo = g.get_repo(full_name)
    except GithubException as e:
        raise ValueError(f"Could not access repository '{full_name}': {e.data.get('message', str(e))}")

    # --- 1. Basic metadata ---
    metadata = {
        "full_name": repo.full_name,
        "name": repo.name,
        "description": repo.description or "No description provided",
        "homepage": repo.homepage or "",
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "open_issues": repo.open_issues_count,
        "watchers": repo.subscribers_count,
        "default_branch": repo.default_branch,
        "license": repo.license.name if repo.license else "Not specified",
        "topics": repo.get_topics(),
        "created_at": str(repo.created_at),
        "updated_at": str(repo.updated_at),
        "is_fork": repo.fork,
        "html_url": repo.html_url,
    }

    # --- 2. Languages ---
    languages = repo.get_languages()

    # --- 3. File tree ---
    tree = _build_tree(repo)
    file_tree_str = _format_tree(tree)

    # --- 4. Important file contents ---
    important_file_contents = {}
    for file_path in IMPORTANT_FILES:
        content = _read_file_content(repo, file_path)
        if content:
            important_file_contents[file_path] = content

    # --- 5. Existing README ---
    existing_readme = None
    for readme_name in ["README.md", "readme.md", "README.rst", "README.txt", "README"]:
        content = _read_file_content(repo, readme_name)
        if content:
            existing_readme = content
            break

    g.close()

    return {
        "metadata": metadata,
        "languages": dict(languages),
        "file_tree": file_tree_str,
        "important_files": important_file_contents,
        "existing_readme": existing_readme,
    }
