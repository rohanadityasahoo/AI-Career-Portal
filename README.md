# AI Career Portal – College Project

**AI Career Portal** is a student‑developed web application that showcases the use of artificial intelligence for career‑related services. The project was created as part of the **[Your Course Name]** at **[Your College/University]** and demonstrates the integration of machine‑learning models, Flask, and modern front‑end design.

---

## 📚 Project Overview

- **Resume Analyzer** – Parses uploaded resumes, extracts key skills, and provides AI‑generated feedback.
- **Career Roadmap Generator** – Suggests personalized learning paths based on user interests and current skill gaps.
- **Interview Simulator** – An interactive chatbot that conducts mock interviews and offers performance insights.
- **Job Matcher & Application Tracker** – Matches user profiles with job listings and tracks application status.
- **Report Generation** – Automatically creates project documentation, technical reports, and presentation decks.

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | **Python 3.12**, **Flask**, **SQLAlchemy** |
| AI/ML | **Transformers** (Hugging Face), **scikit‑learn**, custom PyTorch models |
| Database | **SQLite** (development) – can be swapped for PostgreSQL |
| Front‑end | **HTML5**, **CSS3**, **Bootstrap**, **JavaScript** |
| DevOps | **Git**, **GitHub Actions** for CI, **venv** for isolated environment |

---

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/rohanadityasahoo/AI-Career-Portal.git
   cd AI-Career-Portal
   ```
2. **Create a virtual environment & install dependencies**
   ```bash
   python -m venv venv
   .\\venv\\Scripts\\activate   # on Windows
   pip install -r requirements.txt
   ```
3. **Run the application**
   ```bash
   flask run
   ```
   The app will be available at `http://127.0.0.1:5000`.

---

## 🎓 Academic Context

- **Course:** *[Course Code – Course Title]*
- **Instructor:** *[Instructor Name]*
- **Semester:** *[Fall/Spring] 2026*
- **Team:** *[Your Name]* (and any teammates)
- **Objective:** Demonstrate end‑to‑end AI integration in a web service, covering data preprocessing, model inference, and UI/UX design.

---

## 📂 Repository Structure

```
AI-Career-Portal/
├─ ai_modules/          # Core AI utilities (resume parsing, roadmap, etc.)
├─ database/            # SQLite DB scripts and schema
├─ routes/              # Flask route handlers
├─ static/              # CSS, JS, images
├─ templates/           # Jinja2 HTML templates
├─ outputs/             # Generated reports & presentations
├─ tmp/                 # Temporary files used during processing
├─ file_list.txt        # Auto‑generated list of project files
├─ README.md            # **This file**
└─ app.py               # Flask application entry point
```

---

## 🤝 Contributing

Feel free to fork the repository and submit pull requests. Contributions may include:
- Adding new AI models or improving existing ones.
- Enhancing the UI/UX.
- Refactoring code for better modularity.
- Updating documentation.

---

## 📜 License

This project is released under the **MIT License** – see the `LICENSE` file for details.

---

*Created for academic purposes; not intended for commercial deployment.*
