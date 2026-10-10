"""Private, deterministic resume-text extraction and evidence helpers.

The functions here deliberately do not make hiring decisions. They turn the
text that was successfully extracted from a PDF into a small, auditable set of
signals which the AI reviewer can use as guardrails.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

import pdfplumber


MAX_PAGES = 12
MAX_EXTRACTED_CHARACTERS = 30_000

SECTION_PATTERNS = {
    "Contact details": r"\b(email|phone|mobile|linkedin|github|portfolio)\b",
    "Professional summary": r"\b(summary|profile|objective|about me)\b",
    "Experience": r"\b(experience|employment|work history|internship)\b",
    "Education": r"\b(education|academic background|qualifications)\b",
    "Skills": r"\b(technical skills|skills|competencies|technologies)\b",
    "Projects": r"\b(projects|personal projects|academic projects)\b",
    "Certifications": r"\b(certifications|certificates|courses|training)\b",
}

# These are intentionally recognisable, explicit terms rather than an attempt
# to infer a skill from unrelated prose. They are used for evidence and job
# description comparison, never to claim that a candidate has a skill.
SKILL_PATTERNS = {
    "Python": r"\bpython\b", "Java": r"\bjava\b",
    "JavaScript": r"\bjavascript\b|\bjs\b", "TypeScript": r"\btypescript\b|\bts\b",
    "C++": r"\bc\+\+\b", "C": r"(?<![\w+])c(?![\w+])",
    "C#": r"\bc#\b|\bc sharp\b", "SQL": r"\bsql\b",
    "HTML": r"\bhtml\b", "CSS": r"\bcss\b", "React": r"\breact(?:\.js)?\b",
    "Angular": r"\bangular\b", "Vue": r"\bvue(?:\.js)?\b",
    "Node.js": r"\bnode(?:\.js)?\b", "Flask": r"\bflask\b",
    "Django": r"\bdjango\b", "FastAPI": r"\bfastapi\b",
    "Spring Boot": r"\bspring boot\b", "REST APIs": r"\brest(?:ful)?\s+api(?:s)?\b",
    "Git": r"\bgit\b", "GitHub": r"\bgithub\b", "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b|\bk8s\b", "AWS": r"\baws\b|\bamazon web services\b",
    "Azure": r"\bazure\b", "Google Cloud": r"\bgcp\b|\bgoogle cloud\b",
    "Linux": r"\blinux\b", "MySQL": r"\bmysql\b",
    "PostgreSQL": r"\bpostgres(?:ql)?\b", "MongoDB": r"\bmongodb\b|\bmongo\b",
    "Redis": r"\bredis\b", "Pandas": r"\bpandas\b", "NumPy": r"\bnumpy\b",
    "Power BI": r"\bpower\s*bi\b", "Tableau": r"\btableau\b", "Excel": r"\bexcel\b",
    "Machine Learning": r"\bmachine learning\b|\bml\b", "Deep Learning": r"\bdeep learning\b",
    "TensorFlow": r"\btensorflow\b", "PyTorch": r"\bpytorch\b",
    "Data Analysis": r"\bdata analy(?:sis|tics)\b", "Agile": r"\bagile\b",
    "Scrum": r"\bscrum\b", "Jira": r"\bjira\b", "Figma": r"\bfigma\b",
    "Selenium": r"\bselenium\b", "pytest": r"\bpytest\b",
}

ACTION_VERBS = {
    "achieved", "analyzed", "architected", "automated", "built", "collaborated",
    "created", "delivered", "designed", "developed", "engineered", "implemented",
    "improved", "increased", "launched", "led", "managed", "optimized", "reduced",
    "researched", "streamlined", "tested", "trained",
}


def extract_resume_text(pdf_path: str) -> str:
    """Extract readable text from a PDF while bounding work and retained data."""
    extracted_pages: list[str] = []
    total_characters = 0
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:MAX_PAGES]:
                page_text = _normalise_text(page.extract_text(x_tolerance=2, y_tolerance=3) or "")
                if not page_text:
                    continue
                remaining = MAX_EXTRACTED_CHARACTERS - total_characters
                if remaining <= 0:
                    break
                extracted_pages.append(page_text[:remaining])
                total_characters += len(extracted_pages[-1])
    except Exception:
        # PDFs can fail in third-party parsers in many library-specific ways.
        # Do not expose parser internals or document contents to the browser.
        return ""
    return "\n".join(extracted_pages).strip()


def build_resume_snapshot(resume_text: str, job_description: str = "") -> dict:
    """Return a transparent, heuristic snapshot based only on extracted text.

    Scores are diagnostic indicators, not predictions of ATS behaviour or
    employment outcomes. Keeping them local makes the baseline available when
    an AI provider is unavailable and prevents a model from inventing metrics.
    """
    text = _normalise_text(resume_text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    words = re.findall(r"[A-Za-z][A-Za-z+#./-]*", text)
    detected_skills = _matched_skills(text)
    job_skills = _matched_skills(job_description)
    matched_job_skills = [skill for skill in job_skills if skill in detected_skills]

    bullet_lines = [line for line in lines if re.match(r"^(?:[-•‣▪*]|\d+[.)])\s+", line)]
    action_pattern = r"^(?:[-•‣▪*]|\d+[.)])\s+(?:[A-Z][a-z]+\s+)?(?:" + "|".join(sorted(ACTION_VERBS)) + r")\b"
    action_lines = [line for line in bullet_lines if re.match(action_pattern, line, re.IGNORECASE)]
    metric_lines = [
        line for line in bullet_lines
        if re.search(r"(?:\b\d+(?:\.\d+)?\s*(?:%|x|hours?|days?|weeks?|months?|users?|clients?|records?|projects?)\b|\b\d+[,+]\d+)", line, re.IGNORECASE)
    ]

    has_email = bool(re.search(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b", text))
    has_phone = bool(re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text))
    has_link = bool(re.search(r"\b(?:linkedin\.com|github\.com|https?://|www\.)", text, re.IGNORECASE))
    sections = {
        name: _has_section(lines, pattern)
        for name, pattern in SECTION_PATTERNS.items()
        if name != "Contact details"
    }
    sections["Contact details"] = has_email or has_phone or has_link
    required_sections = ("Experience", "Education", "Skills", "Projects")
    section_score = round(100 * sum(sections[name] for name in required_sections) / len(required_sections))
    contact_score = (has_email + has_phone + has_link) / 3
    keyword_score = min(len(detected_skills) / 10, 1)
    ats_score = round(100 * (0.45 * (section_score / 100) + 0.25 * contact_score + 0.30 * keyword_score))
    content_score = round(100 * min(1, 0.25 * min(len(words) / 300, 1) + 0.20 * min(len(bullet_lines) / 8, 1) + 0.30 * min(len(action_lines) / 5, 1) + 0.25 * min(len(metric_lines) / 3, 1)))
    skill_score = round(100 * keyword_score)
    job_match = round(100 * len(matched_job_skills) / len(job_skills)) if job_skills else None

    observations = _build_observations(
        sections=sections, has_email=has_email, has_phone=has_phone, has_link=has_link,
        word_count=len(words), bullet_count=len(bullet_lines), action_count=len(action_lines),
        metric_count=len(metric_lines), detected_skills=detected_skills,
    )
    return {
        "scores": {"ATS readiness": ats_score, "Section coverage": section_score, "Content evidence": content_score, "Skill visibility": skill_score},
        "sections": sections, "detected_skills": detected_skills, "job_skills": job_skills,
        "matched_job_skills": matched_job_skills, "job_match": job_match,
        "facts": {"word_count": len(words), "bullet_count": len(bullet_lines), "action_bullet_count": len(action_lines), "metric_bullet_count": len(metric_lines), "has_email": has_email, "has_phone": has_phone, "has_link": has_link},
        "observations": observations,
    }


def _matched_skills(text: str) -> list[str]:
    if not text:
        return []
    return [skill for skill, pattern in SKILL_PATTERNS.items() if re.search(pattern, text, re.IGNORECASE)]


def _has_section(lines: Iterable[str], pattern: str) -> bool:
    """Detect a conventional section heading without treating body prose as one."""
    for line in lines:
        candidate = line.strip().rstrip(":").strip()
        # Long sentences that happen to contain "skills" or "experience" are
        # content, not section labels. Most resume headings are short lines.
        if len(candidate) <= 48 and re.fullmatch(pattern, candidate, re.IGNORECASE):
            return True
    return False


def _build_observations(*, sections: dict[str, bool], has_email: bool, has_phone: bool, has_link: bool, word_count: int, bullet_count: int, action_count: int, metric_count: int, detected_skills: Iterable[str]) -> list[str]:
    observations: list[str] = []
    missing_sections = [name for name in ("Experience", "Education", "Skills", "Projects") if not sections[name]]
    if missing_sections:
        observations.append("No clear " + ", ".join(missing_sections) + " heading was detected.")
    if not has_email:
        observations.append("No email address was detected in the extracted text.")
    if not has_phone:
        observations.append("No phone number was detected in the extracted text.")
    if not has_link:
        observations.append("No portfolio, LinkedIn, or GitHub link was detected in the extracted text.")
    if word_count < 180:
        observations.append("The extracted text is brief; add relevant detail only where it is truthful.")
    if bullet_count < 4:
        observations.append("Few bullet points were detected; concise bullets can make achievements easier to scan.")
    if action_count < 3:
        observations.append("Few action-led bullets were detected.")
    if metric_count < 2:
        observations.append("Few quantified outcomes were detected; add numbers only when you can verify them.")
    if not list(detected_skills):
        observations.append("No skills from the supported evidence list were detected; use a clearly labelled skills section.")
    return observations[:6]


def _normalise_text(value: str) -> str:
    value = str(value or "").replace("\x00", " ").replace("\r", "\n")
    value = re.sub(r"[\t\f\v ]+", " ", value)
    return re.sub(r"\n{3,}", "\n\n", value).strip()
