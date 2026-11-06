"""Turn extracted resume text into bounded, structured candidate data."""

from __future__ import annotations

import re


SECTION_ALIASES = {
    "summary": {"summary", "professional summary", "profile", "objective", "about me"},
    "experience": {"experience", "work experience", "employment", "work history", "internship", "internships"},
    "education": {"education", "academic background", "qualifications", "academic qualifications"},
    "skills": {"skills", "technical skills", "core skills", "competencies", "technologies"},
    "projects": {"projects", "personal projects", "academic projects", "key projects"},
    "certifications": {"certifications", "certificates", "courses", "training"},
    "achievements": {"achievements", "awards", "activities", "leadership"},
}

SECTION_LABELS = {
    "summary": "Professional Summary",
    "skills": "Skills",
    "experience": "Experience",
    "projects": "Projects",
    "education": "Education",
    "certifications": "Certifications",
    "achievements": "Achievements",
}

MAX_TEXT = 12_000


def _clean_text(value, limit=MAX_TEXT):
  value = re.sub(r"[ \t]+", " ", str(value or "")).strip()
  return value[:limit]


def _normalise_heading(value):
  value = re.sub(r"[^a-z ]", " ", str(value or "").lower())
  return re.sub(r"\s+", " ", value).strip()


def _section_for_line(line):
  heading = _normalise_heading(line)
  for section, aliases in SECTION_ALIASES.items():
    if heading in aliases:
      return section
  return None


def _split_skills(value):
  skills = []
  for item in re.split(r"[,;|\n]", str(value or "")):
    item = re.sub(r"^[^:]{1,35}:\s*", "", item.strip())
    item = re.sub(r"\s+", " ", item)
    if item and item not in skills:
      skills.append(item[:90])
  return skills[:80]


def _first_name(lines):
  for line in lines[:8]:
    lowered = line.lower()
    if (
        not line
        or _section_for_line(line)
        or "@" in line
        or re.search(r"https?://|www\.|linkedin\.com|github\.com", lowered)
        or re.search(r"\b(?:resume|curriculum vitae|cv)\b", lowered)
        or re.search(r"\d{5,}", line)
    ):
      continue
    return line[:180]
  return ""


def parse_resume_text(resume_text):
  """Return contact details and canonical resume sections from extracted text."""
  text = str(resume_text or "").replace("\r\n", "\n").replace("\r", "\n")
  lines = [line.strip() for line in text.splitlines() if line.strip()]
  sections = {key: "" for key in SECTION_ALIASES}
  section_lines = {key: [] for key in SECTION_ALIASES}
  preamble = []
  current_section = None

  for line in lines:
    section = _section_for_line(line)
    if section:
      current_section = section
      continue
    if current_section:
      section_lines[current_section].append(line)
    else:
      preamble.append(line)

  for key, values in section_lines.items():
    sections[key] = "\n".join(values[:80]).strip()[:MAX_TEXT]

  email_match = re.search(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b", text)
  phone_match = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", "\n".join(preamble[:8]))
  links = re.findall(
      r"(?:https?://|www\.)\S+|(?:linkedin\.com|github\.com)/\S+",
      text,
      re.IGNORECASE,
  )
  links = [link.rstrip(".,)")[:240] for link in links[:5]]
  contact_parts = []
  if email_match:
    contact_parts.append(email_match.group(0))
  if phone_match:
    contact_parts.append(re.sub(r"\s+", " ", phone_match.group(0)).strip())
  contact_parts.extend(link for link in links if link not in contact_parts)

  location = ""
  for line in preamble[:8]:
    if "," in line and not re.search(r"@|https?://|\d{5,}", line):
      location = line[:160]
      break

  contact_line = " | ".join(contact_parts)
  if location and location not in contact_line:
    contact_line = f"{location} | {contact_line}" if contact_line else location

  return {
      "name": _first_name(preamble),
      "contact": {
          "email": email_match.group(0) if email_match else "",
          "phone": phone_match.group(0).strip() if phone_match else "",
          "links": links,
          "location": location,
          "line": contact_line[:500],
      },
      "skills": _split_skills(sections["skills"]),
      "sections": sections,
      "source_text": text[:MAX_TEXT],
  }


def build_resume_draft(parsed_resume, role="", skill_line="", profile_type="fresher"):
  """Create a truthful draft baseline before the AI writer improves wording."""
  parsed_resume = parsed_resume or {}
  sections = parsed_resume.get("sections") or {}
  contact = parsed_resume.get("contact") or {}
  experienced = profile_type == "experienced"
  role = _clean_text(role, 120) or (
      "your target role" if experienced else "your target entry-level role"
  )
  skills = _clean_text(sections.get("skills"), 700)
  skills = skills or _clean_text(skill_line, 700)
  skills = skills or "[Add the technical skills you can prove]"

  return {
      "name": _clean_text(parsed_resume.get("name"), 180) or "[Full name]",
      "contact": _clean_text(contact.get("line"), 500) or "[City, State] | [professional email] | [phone] | [LinkedIn] | [GitHub or portfolio]",
      "headline": f"{role}",
      "summary": _clean_text(sections.get("summary"), 900) or (
          f"Working professional targeting {role} with evidence of {skills}. "
          "Add measurable scope, ownership, and one truthful result before applying."
          if experienced else
          f"Entry-level candidate targeting {role} with evidence of {skills}. "
          "Add your strongest project, education, and one truthful result before applying."
      ),
      "skills": skills,
      "education": _clean_text(sections.get("education"), 1_200) or (
          "[Degree or current program] in [Discipline] | [College or university] | "
          "[Graduation month and year]"
      ),
      "projects": _clean_text(sections.get("projects"), 2_400) or (
          f"[Project name] | {skills}\n"
          "- Built [what you created] to solve [specific problem or user need].\n"
          "- Implemented [your contribution] using [tools or methods].\n"
          "- Result: [verified outcome, scale, performance change, or learning result]."
      ),
      "experience": _clean_text(sections.get("experience"), 1_800) or (
          "[Role] | [Organization] | [Dates]\n"
          "- [Action] [scope or responsibility] using [tool or method].\n"
          "- [Action] [business outcome] and achieved [verified result]."
          if experienced else
          "[Internship, freelance, volunteer, campus, or practice role] | [Organization] | [Dates]\n"
          "- [Action] [task or contribution] using [tool or method].\n"
          "- [Action] [second contribution] and achieved [verified result]."
      ),
      "certifications": _clean_text(sections.get("certifications"), 1_000) or "",
      "achievements": _clean_text(sections.get("achievements"), 1_000) or "",
  }
