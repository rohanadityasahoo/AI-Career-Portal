"""Build a grounded, all-in-one resume package for fresher candidates."""

from ai_modules.resume_parser import build_resume_draft, parse_resume_text


def _clean(value, limit=320):
  return " ".join(str(value or "").split())[:limit]


def _role_label(feedback, target_role):
  role = _clean(target_role, 120)
  if role:
    return role
  for item in feedback.get("suggested_roles", []):
    if isinstance(item, dict) and _clean(item.get("role"), 120):
      return _clean(item.get("role"), 120)
  return "your target entry-level role"


def _readiness(score):
  score = int(score or 0)
  if score >= 75:
    return {
        "label": "Strong foundation",
        "tone": "positive",
        "message": "Your resume has a useful base. Polish the highest-impact gaps before applying.",
    }
  if score >= 55:
    return {
        "label": "Ready to polish",
        "tone": "steady",
        "message": "You have usable evidence, but a few focused changes will make it easier to trust and scan.",
    }
  return {
      "label": "Build the evidence",
      "tone": "attention",
      "message": "Start with the missing sections and turn your projects or coursework into clear proof of ability.",
  }


def _missing_section_actions(feedback):
  section_guidance = {
      "Contact details": "Add a professional email, phone number, city, LinkedIn, and portfolio or GitHub link where relevant.",
      "Professional summary": "Add a short, role-focused summary that names your education, strongest evidence, and target direction.",
      "Experience": "If you have no formal job history, use internships, freelance work, volunteering, campus roles, or relevant practice work.",
      "Education": "Show your degree or current program, institution, location, graduation timing, and relevant coursework if useful.",
      "Skills": "Add a clear skills section and connect each important skill to a project, course, internship, or work sample.",
      "Projects": "Add two or three relevant projects with the problem, your contribution, tools used, and a truthful result or learning outcome.",
      "Certifications": "Add relevant certifications, courses, or training with the issuer and completion year; omit this section if none apply.",
  }
  missing = []
  for section, found in (feedback.get("sections") or {}).items():
    if not found and section in section_guidance:
      missing.append({"title": f"Complete {section}", "body": section_guidance[section]})
  return missing[:4]


def _local_resume_draft(role, skill_line, resume_text, parsed_resume=None):
  parsed_resume = parsed_resume or parse_resume_text(resume_text)
  return build_resume_draft(parsed_resume, role, skill_line)


def _resume_draft(feedback, role, skill_line, resume_text, parsed_resume=None, target_company=""):
  fallback = _local_resume_draft(role, skill_line, resume_text, parsed_resume)
  supplied = feedback.get("resume_draft") or {}
  if not isinstance(supplied, dict):
    return fallback, "Drafted from uploaded resume"
  draft = dict(fallback)
  for key in fallback:
    value = supplied.get(key)
    if isinstance(value, str) and value.strip():
      draft[key] = value.strip()
  if "resume_writer_assisted" in feedback:
    label = (
        "AI-drafted and job-tailored from uploaded resume"
        if feedback.get("resume_writer_assisted")
        else "Parser-drafted from uploaded resume"
    )
  else:
    label = "AI-drafted from uploaded resume" if feedback.get("ai_assisted") else "Drafted from uploaded resume"
  return draft, label


def build_fresher_resume_package(
    feedback,
    target_role="",
    resume_text="",
    parsed_resume=None,
    target_company="",
):
  """Return a grounded ATS-friendly resume package for a fresher candidate."""
  feedback = feedback or {}
  role = _role_label(feedback, target_role)
  skills = [
      _clean(skill, 70)
      for skill in (feedback.get("detected_skills") or [])
      if _clean(skill, 70)
  ][:8]
  skill_line = ", ".join(skills) or "[Add the technical skills you can prove]"
  job_alignment = feedback.get("job_alignment") or {}
  missing_role_skills = [
      _clean(skill, 70)
      for skill in (job_alignment.get("missing_skills") or [])
      if _clean(skill, 70)
  ][:8]
  actions = [
      _clean(item.get("title"), 120)
      for item in (feedback.get("priority_actions") or [])
      if isinstance(item, dict) and _clean(item.get("title"), 120)
  ][:4]
  strengths = [
      _clean(item, 240)
      for item in (feedback.get("strengths") or [])
      if _clean(item, 240)
  ][:3]
  resume_draft, draft_label = _resume_draft(
      feedback,
      role,
      skill_line,
      resume_text,
      parsed_resume,
      target_company=target_company,
  )

  return {
      "role": role,
      "target_company": _clean(target_company, 160),
      "draft_label": draft_label,
      "ats_optimization": {
          "title": "ATS-friendly structure applied",
          "checks": [
              "Conventional section headings",
              "Target-role language in the headline and summary",
              "Plain-text, single-column copy blocks",
              "Skills connected to projects or practical evidence",
          ],
          "note": "No tool can honestly guarantee a universal 100/100 ATS score. ATS results vary by employer, job description, parser, and formatting rules. This draft is optimized for common ATS signals without inventing facts.",
      },
      "readiness": _readiness(feedback.get("overall_score")),
      "must_fix": _missing_section_actions(feedback),
      "top_actions": actions,
      "strengths": strengths,
      "job_keywords": missing_role_skills,
      "resume_draft": resume_draft,
      "application_kit": {
          "cover_letter": (
              f"Dear Hiring Manager,\n\n"
              f"I am applying for the {role} opportunity. I am an entry-level candidate with resume evidence of {skill_line}. "
              "My strongest proof is [name your most relevant project, internship, or coursework], where I [describe your contribution] and [state a truthful result or learning outcome].\n\n"
              "I would welcome the opportunity to bring this foundation to your team and continue learning in a practical environment. "
              "Thank you for your consideration.\n\n"
              "Sincerely,\n[Your name]"
          ),
          "recruiter_message": (
              f"Hi [Recruiter name], I am an entry-level candidate interested in {role}. "
              f"My resume highlights {skill_line} and [one relevant project or result]. "
              "I would appreciate the opportunity to be considered. Thank you."
          ),
          "linkedin_about": (
              f"I am an entry-level candidate building toward {role}. My current resume evidence includes {skill_line}. "
              "I enjoy turning coursework and projects into practical solutions, and I am actively looking for opportunities to learn, contribute, and grow. "
              "I am especially interested in [industry, problem area, or type of team]."
          ),
      },
      "plan": [
          {
              "week": "Week 1",
              "focus": "Make the resume complete",
              "tasks": [
                  "Fill every bracketed placeholder with a truthful fact.",
                  "Complete contact details, education, skills, and project sections.",
                  "Remove unrelated or repeated content.",
              ],
          },
          {
              "week": "Week 2",
              "focus": "Strengthen practical proof",
              "tasks": [
                  "Rewrite the two strongest projects using action, tools, and result.",
                  "Add a GitHub, portfolio, demo, or document link where available.",
                  "Connect each important skill to evidence in the resume.",
              ],
          },
          {
              "week": "Week 3",
              "focus": "Target one role",
              "tasks": [
                  f"Compare the resume with three {role} job descriptions.",
                  "Add only missing keywords that you genuinely understand or can support.",
                  "Prepare one tailored resume version for the strongest role direction.",
              ],
          },
          {
              "week": "Week 4",
              "focus": "Start applying with consistency",
              "tasks": [
                  "Send applications with the matching cover letter and recruiter message.",
                  "Track applications, follow-ups, and interview preparation.",
                  "Review results weekly and improve the resume using real feedback.",
              ],
          },
      ],
      "truth_note": "Use the draft as a starting point. Replace every bracketed item and keep only claims, skills, numbers, and outcomes you can verify.",
  }
