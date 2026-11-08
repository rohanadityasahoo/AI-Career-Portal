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
    "Professional summary": r"(?:professional\s+)?(?:summary|profile|objective|about\s+me|career\s+summary)",
    "Experience": r"(?:professional\s+)?(?:experience|employment|work\s+history|work\s+experience|internships?)",
    "Education": r"(?:education|academic\s+background|qualifications)",
    "Skills": r"(?:technical\s+skills|skills|competencies|technologies|core\s+skills)",
    "Projects": r"(?:projects|personal\s+projects|academic\s+projects|selected\s+projects)",
    "Certifications": r"(?:certifications|certificates|courses|training|professional\s+development)",
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
    "researched", "streamlined", "tested", "trained", "maintained", "performed",
    "validated", "supported", "coordinated", "resolved", "facilitated", "mentored",
    "owned", "oversaw", "conducted", "deployed", "migrated", "negotiated",
}

METRIC_PATTERN = re.compile(
    r"(?<!\w)(?:"
    r"\d+(?:\.\d+)?\s*%|"
    r"\d+(?:\.\d+)?\s*(?:x|times|hours?|days?|weeks?|months?|years?|users?|clients?|customers?|records?|projects?|tickets?|cases?)\b|"
    r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|"
    r"\d+(?:\.\d+)?\s*\+|"
    r"(?:[$]|USD|EUR|GBP|INR)\s*\d+(?:\.\d+)?\s*[kmb]?"
    r")(?!\w)",
    re.IGNORECASE,
)


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


def build_resume_snapshot(resume_text: str, job_description: str = "", profile_type: str = "fresher") -> dict:
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

    bullet_lines = [line for line in lines if re.match(r"^(?:[-•‣▪*◦●]|\d+[.)])\s+", line)]
    action_pattern = r"^(?:[-•‣▪*◦●]|\d+[.)])\s+(?:(?:successfully|independently|directly|proactively|consistently|effectively)\s+)?(?:" + "|".join(sorted(ACTION_VERBS)) + r")\b"
    action_lines = [line for line in bullet_lines if re.match(action_pattern, line, re.IGNORECASE)]
    metric_lines = [line for line in bullet_lines if METRIC_PATTERN.search(line)]

    has_email = bool(re.search(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b", text))
    has_phone = _has_phone_number(text)
    has_link = bool(re.search(r"\b(?:linkedin\.com|github\.com|behance\.net|dribbble\.com|portfolio|https?://|www\.)", text, re.IGNORECASE))
    sections = {
        name: _has_section(lines, pattern)
        for name, pattern in SECTION_PATTERNS.items()
        if name != "Contact details"
    }
    sections["Contact details"] = has_email or has_phone or has_link
    profile_type = "experienced" if profile_type == "experienced" else "fresher"
    contact_score = (has_email + has_phone + has_link) / 3
    keyword_score = min(len(detected_skills) / 10, 1)
    skill_score = round(100 * (0.75 * keyword_score + 0.25 * int(sections.get("Skills", False))))
    job_match = round(100 * len(matched_job_skills) / len(job_skills)) if job_skills else None
    if profile_type == "experienced":
        required_sections = ("Professional summary", "Experience", "Skills")
        profile_focus = "Professional impact"
        section_score = round(100 * sum(sections[name] for name in required_sections) / len(required_sections))
        content_score = round(100 * min(1, 0.15 * min(len(words) / 450, 1) + 0.30 * min(len(bullet_lines) / 10, 1) + 0.30 * min(len(action_lines) / 6, 1) + 0.25 * min(len(metric_lines) / 4, 1)))
    else:
        required_sections = ("Education", "Projects", "Skills")
        profile_focus = "Entry-level readiness"
        section_score = round(100 * sum(sections[name] for name in required_sections) / len(required_sections))
        content_score = round(100 * min(1, 0.30 * min(len(words) / 350, 1) + 0.30 * min(len(bullet_lines) / 8, 1) + 0.20 * min(len(action_lines) / 5, 1) + 0.20 * min(len(metric_lines) / 3, 1)))

    if job_match is not None:
        ats_score = round(100 * (
            0.30 * (section_score / 100)
            + 0.15 * contact_score
            + 0.20 * (skill_score / 100)
            + 0.20 * (content_score / 100)
            + 0.15 * (job_match / 100)
        ))
        overall_score = round(
            0.30 * ats_score
            + 0.20 * section_score
            + 0.20 * content_score
            + 0.15 * skill_score
            + 0.15 * job_match
        )
    else:
        if profile_type == "experienced":
            ats_score = round(100 * (0.35 * (section_score / 100) + 0.20 * contact_score + 0.20 * (skill_score / 100) + 0.25 * (content_score / 100)))
        else:
            ats_score = round(100 * (0.40 * (section_score / 100) + 0.20 * contact_score + 0.25 * (skill_score / 100) + 0.15 * (content_score / 100)))
        overall_score = round(
            0.35 * ats_score
            + 0.25 * section_score
            + 0.25 * content_score
            + 0.15 * skill_score
        )

    observations = _build_observations(
        sections=sections, has_email=has_email, has_phone=has_phone, has_link=has_link,
        word_count=len(words), bullet_count=len(bullet_lines), action_count=len(action_lines),
        metric_count=len(metric_lines), detected_skills=detected_skills,
        profile_type=profile_type, required_sections=required_sections,
    )
    score_gaps = _build_score_gaps(
        scores={
            "ATS readiness": ats_score,
            "Section coverage": section_score,
            "Content evidence": content_score,
            "Skill visibility": skill_score,
        },
        sections=sections,
        required_sections=required_sections,
        facts={
            "word_count": len(words),
            "bullet_count": len(bullet_lines),
            "action_bullet_count": len(action_lines),
            "metric_bullet_count": len(metric_lines),
            "has_email": has_email,
            "has_phone": has_phone,
            "has_link": has_link,
        },
        detected_skill_count=len(detected_skills),
        job_match=job_match,
        profile_type=profile_type,
    )
    return {
        "profile_type": profile_type, "profile_focus": profile_focus,
        "required_sections": required_sections,
        "overall_score": overall_score,
        "scores": {"ATS readiness": ats_score, "Section coverage": section_score, "Content evidence": content_score, "Skill visibility": skill_score},
        "sections": sections, "detected_skills": detected_skills, "job_skills": job_skills,
        "matched_job_skills": matched_job_skills, "job_match": job_match,
        "facts": {"word_count": len(words), "bullet_count": len(bullet_lines), "action_bullet_count": len(action_lines), "metric_bullet_count": len(metric_lines), "has_email": has_email, "has_phone": has_phone, "has_link": has_link},
        "observations": observations,
        "overall_score_gaps": score_gaps["overall"],
        "ats_score_gaps": score_gaps["ats"],
    }


def _build_score_gaps(*, scores, sections, required_sections, facts, detected_skill_count, job_match, profile_type):
    """Explain the concrete evidence thresholds behind both displayed scores."""
    experienced = profile_type == "experienced"
    word_target = 450 if experienced else 350
    bullet_target = 10 if experienced else 8
    action_target = 6 if experienced else 5
    metric_target = 4 if experienced else 3
    gaps = []

    def add_gap(category, current, target, action, score_key):
        current = int(current)
        target = int(target)
        if current < target:
            gaps.append({
                "category": category,
                "current": current,
                "target": target,
                "shortfall": target - current,
                "action": action,
                "score_key": score_key,
            })

    missing_sections = [name for name in required_sections if not sections.get(name)]
    if missing_sections:
        add_gap(
            "Required sections",
            len(required_sections) - len(missing_sections),
            len(required_sections),
            "Add clear conventional headings for: " + ", ".join(missing_sections) + ".",
            "Section coverage",
        )
    add_gap("Resume detail", facts["word_count"], word_target, f"Add relevant, truthful detail until the resume has about {word_target} words.", "Content evidence")
    add_gap("Bullet points", facts["bullet_count"], bullet_target, f"Use at least {bullet_target} concise bullets for measurable work, projects, or achievements.", "Content evidence")
    add_gap("Action-led bullets", facts["action_bullet_count"], action_target, f"Start at least {action_target} bullets with clear action verbs and describe your contribution.", "Content evidence")
    add_gap("Quantified outcomes", facts["metric_bullet_count"], metric_target, f"Add {metric_target} verified numbers showing scale, time, users, results, or impact.", "Content evidence")
    add_gap("Visible skills", detected_skill_count, 10, "List up to 10 relevant skills you can prove in the resume; do not add unsupported keywords.", "Skill visibility")
    if job_match is not None:
        add_gap("Job keyword alignment", job_match, 100, "Match the job description's relevant keywords only where your resume contains truthful supporting evidence.", "ATS readiness")
    contact_current = sum(bool(facts[key]) for key in ("has_email", "has_phone", "has_link"))
    add_gap("Contact essentials", contact_current, 3, "Include a professional email, phone number, and LinkedIn, GitHub, or portfolio link.", "ATS readiness")

    return {"overall": gaps, "ats": list(gaps)}


def _matched_skills(text: str) -> list[str]:
    if not text:
        return []
    return [skill for skill, pattern in SKILL_PATTERNS.items() if re.search(pattern, text, re.IGNORECASE)]


def _has_phone_number(text: str) -> bool:
    """Avoid treating years and date ranges as phone numbers."""
    candidates = re.findall(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)", text)
    for candidate in candidates:
        digits = re.sub(r"\D", "", candidate)
        separators = len(re.findall(r"[\s().-]", candidate))
        year_chunks = re.findall(r"\b(?:19|20)\d{2}\b", candidate)
        if len(year_chunks) >= 2 and len(digits) == len(year_chunks) * 4:
            continue
        if 7 <= len(digits) <= 15 and (len(digits) >= 10 or separators >= 2):
            return True
    return False


def _has_section(lines: Iterable[str], pattern: str) -> bool:
    """Detect a conventional section heading without treating body prose as one."""
    for line in lines:
        candidate = re.sub(r"\s+", " ", line.strip().rstrip(":").strip())
        candidate = re.sub(r"^(?:[-•‣▪*◦●]|\d+[.)])\s+", "", candidate)
        candidate = re.sub(r"\s*(?:\||–|—)\s*", " - ", candidate)
        # Long sentences that happen to contain "skills" or "experience" are
        # content, not section labels. Most resume headings are short lines.
        if len(candidate) <= 60 and re.fullmatch(pattern, candidate, re.IGNORECASE):
            return True
        if len(candidate) <= 60 and re.fullmatch(
            rf"(?:{pattern})(?:\s*(?:&|and|/|-|:)\s*[A-Za-z][A-Za-z ]*)?",
            candidate,
            re.IGNORECASE,
        ):
            return True
    return False


def _build_observations(*, sections: dict[str, bool], has_email: bool, has_phone: bool, has_link: bool, word_count: int, bullet_count: int, action_count: int, metric_count: int, detected_skills: Iterable[str], profile_type: str, required_sections: Iterable[str]) -> list[str]:
    observations: list[str] = []
    missing_sections = [name for name in required_sections if not sections[name]]
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
        if profile_type == "experienced":
            observations.append("Few quantified outcomes were detected; show scale, ownership, or measurable business impact where you can verify it.")
        else:
            observations.append("Few quantified outcomes were detected; quantify project scale or results only when you can verify them.")
    if not list(detected_skills):
        observations.append("No skills from the supported evidence list were detected; use a clearly labelled skills section.")
    return observations[:6]


def _normalise_text(value: str) -> str:
    value = str(value or "").replace("\x00", " ").replace("\r", "\n")
    value = re.sub(r"[\t\f\v ]+", " ", value)
    return re.sub(r"\n{3,}", "\n\n", value).strip()
