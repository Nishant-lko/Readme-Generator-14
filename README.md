
> Generate professional, production-quality README.md files for any GitHub repository in under 15 seconds.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-🦜-1C3C3C)](https://langchain.com)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?logo=google&logoColor=white)](https://ai.google.dev)

---

## ✨ Features

### 🚀 README Generation
- Paste any GitHub repository URL and get a polished README in seconds
- AI analyzes repository metadata, file tree, languages, config files, and existing README
- No cloning required — works entirely via the GitHub API

### 🎨 3 README Styles
| Style | Description |
|-------|-------------|
| **📄 Minimal** | Clean and concise — title, description, install, usage, license |
| **📋 Detailed** | Comprehensive with all standard sections, badges, and project structure |
| **🌟 Awesome** | Eye-catching with emojis, centered banners, ToC, and visual flair |

### 📝 Custom Instructions
Guide the AI with your own instructions:
- *"Focus on the API endpoints"*
- *"Write in a casual, friendly tone"*
- *"Add a deployment section for Docker"*
- *"Emphasize the machine learning pipeline"*

### 📊 README Analyzer
Score any existing README out of 100 with detailed feedback:
- **Quality Score** — Visual score circle with color coding
- **Strengths** — What the README does well
- **Improvements** — Actionable suggestions
- **Missing Sections** — Recommended sections not yet present

### 🔒 Private Repository Support
- Supply your GitHub Personal Access Token to analyze private repos
- Token is used only for the request — never stored or logged

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI (Python) |
| **AI Engine** | LangChain + Google Gemini 2.5 Flash |
| **GitHub Integration** | PyGithub (GitHub REST API) |
| **Frontend** | Vanilla HTML / CSS / JavaScript |
| **Markdown Rendering** | marked.js (CDN) |

---

## 📁 Project Structure

```
README-ai/
├── app.py                  # FastAPI app — routes & server
├── app/
│   ├── __init__.py
│   ├── config.py           # Environment settings (Pydantic)
│   ├── models.py           # Request/Response schemas
│   ├── agents.py           # LangChain chains, prompts & styles
│   └── tools.py            # GitHub API data fetching
├── static/
│   ├── index.html          # Frontend SPA
│   ├── style.css           # Premium dark theme
│   └── script.js           # UI logic, tabs, forms
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Google Gemini API Key](https://aistudio.google.com/apikey)
- GitHub Personal Access Token *(optional, for private repos & higher rate limits)*

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/readme-ai.git
cd readme-ai

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Configuration

Edit the `.env` file:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here    # Optional
GEMINI_MODEL=models/gemini-2.5-flash
```

### Run

```bash
python app.py
```

Open **http://localhost:8000** in your browser.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/styles` | List available README styles |
| `POST` | `/api/generate` | Generate a README |
| `POST` | `/api/analyze` | Analyze an existing README |

### Generate README

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/tiangolo/fastapi",
    "style": "detailed",
    "custom_instructions": "Focus on the API features"
  }'
```

### Analyze README

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/tiangolo/fastapi"
  }'
```

---

## 🎨 UI Preview

- **Dark premium theme** with cyan/teal/purple gradient accents
- **Glassmorphism** effects and smooth animations
- **Tab navigation** — Generate / Analyze
- **Preview & Markdown toggle** for generated output
- **Copy & Download** with one click

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ using LangChain & Google Gemini
</p>
