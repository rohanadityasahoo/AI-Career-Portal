import re
from datetime import date, datetime

from ai_modules.career_tools_ai import (
    cover_letter_draft,
    job_match_insights,
    pipeline_insights,
    skill_gap_insights,
)
from database.db import (
    ensure_auth_schema,
    ensure_career_tools_schema,
    ensure_resume_analysis_schema,
    get_db_connection,
)
from flask import Blueprint, Response, redirect, render_template, request, session, url_for
from ai_modules.usage import ai_feature_context
from routes.auth import login_required

career_tools = Blueprint('career_tools', __name__, url_prefix='/tools')

APPLICATION_STATUSES = (
    'Saved', 'Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn'
)
APPLICATION_PRIORITIES = ('High', 'Medium', 'Low')
WORK_PREFERENCES = ('Remote', 'Hybrid', 'On-site', 'Flexible')

PROFESSIONAL_TOOL_CATALOG = (
    {
        'number': '01', 'slug': 'resume-health',
        'title': 'Resume health dashboard',
        'description': 'See the proof, structure, and ATS signals that need attention before you apply.',
        'kind': 'generic',
    },
    {
        'number': '02', 'slug': 'career-positioning',
        'title': 'Career positioning report',
        'description': 'Turn your current experience into a clear story for the next role you want.',
        'kind': 'generic',
    },
    {
        'number': '03', 'slug': 'job-matcher',
        'title': 'Target role/company match',
        'description': 'Compare your evidence with a real opportunity and see the strongest next move.',
        'endpoint': 'job_matcher',
    },
    {
        'number': '04', 'slug': 'career-switch-planner',
        'title': 'Career switch planner',
        'description': 'Build a realistic bridge from your current role into a new field or function.',
        'kind': 'generic',
    },
    {
        'number': '05', 'slug': 'achievement-extractor',
        'title': 'Achievement extractor',
        'description': 'Find ownership, outcomes, and missing metrics hidden in your experience bullets.',
        'kind': 'generic',
    },
    {
        'number': '06', 'slug': 'resume-editor',
        'title': 'Resume editor',
        'description': 'Open the editable draft, switch templates, review wording, and export your resume.',
        'endpoint': 'resume_tailor',
    },
    {
        'number': '07', 'slug': 'ats-optimizer',
        'title': 'ATS keyword optimizer',
        'description': 'Find the important language from a job post and place it where a recruiter can verify it.',
        'kind': 'generic',
    },
    {
        'number': '08', 'slug': 'linkedin-optimizer',
        'title': 'LinkedIn optimizer',
        'description': 'Draft a focused headline, About section, skills, and proof-building featured section.',
        'kind': 'generic',
    },
    {
        'number': '09', 'slug': 'cover-letter',
        'title': 'Cover-letter generator',
        'description': 'Create a truthful, role-specific cover letter grounded in the evidence you provide.',
        'endpoint': 'cover_letter',
    },
    {
        'number': '10', 'slug': 'recruiter-message',
        'title': 'Recruiter-message generator',
        'description': 'Write a concise outreach message that makes the next step easy to answer.',
        'kind': 'generic',
    },
    {
        'number': '12', 'slug': 'promotion-leadership',
        'title': 'Promotion & leadership analyzer',
        'description': 'Measure how clearly your resume shows scope, influence, leadership, and readiness.',
        'kind': 'generic',
    },
    {
        'number': '13', 'slug': 'career-story',
        'title': 'Career story builder',
        'description': 'Build a confident interview and networking story for an advancement or career switch.',
        'kind': 'generic',
    },
    {
        'number': '14', 'slug': 'skill-gap',
        'title': 'Skill-gap roadmap',
        'description': 'Prioritize the skills and evidence that will make your target role more believable.',
        'endpoint': 'skill_gap',
    },
    {
        'number': '15', 'slug': 'application-tracker',
        'title': 'Job application tracker',
        'description': 'Keep every application, follow-up, interview, and next action in one accountable pipeline.',
        'endpoint': 'application_tracker',
    },
)

PROFESSIONAL_TOOL_CONFIG = {
    'resume-health': {
        'eyebrow': '01 / Resume health',
        'title': 'Know what is holding the resume back.',
        'description': 'Paste the current resume text and get a transparent diagnostic before you rewrite anything.',
        'fields': ('resume_text', 'target_role', 'job_description'),
    },
    'career-positioning': {
        'eyebrow': '02 / Career positioning',
        'title': 'Make the next move easy to understand.',
        'description': 'Clarify the role, field, company, and proof that should lead your professional story.',
        'fields': ('current_role', 'target_role', 'target_field', 'target_company', 'highlights'),
    },
    'career-switch-planner': {
        'eyebrow': '04 / Career switch planner',
        'title': 'Build the bridge, not a random restart.',
        'description': 'Use your existing experience, target field, and role requirements to plan the smallest credible switch.',
        'fields': ('current_role', 'target_role', 'target_field', 'skills', 'highlights'),
    },
    'achievement-extractor': {
        'eyebrow': '05 / Achievement extractor',
        'title': 'Turn responsibilities into evidence.',
        'description': 'Paste experience bullets or notes. The tool identifies ownership, outcomes, and where a metric is still missing.',
        'fields': ('resume_text', 'highlights'),
    },
    'ats-optimizer': {
        'eyebrow': '07 / ATS optimizer',
        'title': 'Align the language without keyword stuffing.',
        'description': 'Compare the job description with your resume evidence and get a short, defensible keyword checklist.',
        'fields': ('target_role', 'job_description', 'resume_text', 'skills'),
    },
    'linkedin-optimizer': {
        'eyebrow': '08 / LinkedIn optimizer',
        'title': 'Make your profile tell the same story.',
        'description': 'Draft the high-signal parts of LinkedIn from your current role, target direction, and real strengths.',
        'fields': ('current_role', 'current_company', 'target_role', 'target_field', 'skills', 'highlights'),
    },
    'recruiter-message': {
        'eyebrow': '10 / Recruiter message',
        'title': 'Start a useful conversation.',
        'description': 'Create a short message that names the role, gives relevant proof, and ends with a clear ask.',
        'fields': ('recruiter_name', 'company', 'target_role', 'highlights'),
    },
    'promotion-leadership': {
        'eyebrow': '12 / Promotion & leadership',
        'title': 'Show scope before you ask for the next level.',
        'description': 'Check whether the resume demonstrates influence, ownership, decision-making, and people or program leadership.',
        'fields': ('current_role', 'target_role', 'resume_text', 'highlights'),
    },
    'career-story': {
        'eyebrow': '13 / Career story builder',
        'title': 'Explain your move with confidence.',
        'description': 'Build a concise story for interviews, networking, and recruiter conversations without inventing a new past.',
        'fields': ('current_role', 'target_role', 'target_field', 'highlights'),
    },
}

PROFESSIONAL_FIELD_LABELS = {
    'resume_text': ('Resume text or experience bullets', 'Paste the text from your current resume.', 'textarea'),
    'target_role': ('Target role', 'e.g. Product Manager or Senior Data Analyst', 'input'),
    'target_field': ('Target field', 'e.g. Banking, Product, Healthcare, or Culinary', 'input'),
    'target_company': ('Target company', 'Optional company you want to join', 'input'),
    'current_role': ('Current role', 'Your current or most recent job title', 'input'),
    'current_company': ('Current company', 'Your current or most recent employer', 'input'),
    'skills': ('Skills', 'Separate skills with commas', 'textarea'),
    'highlights': ('Career highlights', 'Projects, ownership, outcomes, and responsibilities you can verify', 'textarea'),
    'job_description': ('Job description', 'Paste the target job post or requirements', 'textarea'),
    'recruiter_name': ('Recruiter name', 'Optional; leave blank for a general message', 'input'),
    'company': ('Company', 'The company you are contacting', 'input'),
}

SKILL_DETAILS = {
    'Agile': ('Show how you planned, delivered, and improved work in short cycles.', 'Write one delivery story using context, action, and outcome.'),
    'Analytics': ('Explain how you used data to choose a direction or measure an outcome.', 'Add one metric-led case study to your portfolio or resume.'),
    'API testing': ('Demonstrate reliable validation of endpoints, contracts, and error paths.', 'Create an API test collection with positive and negative cases.'),
    'Excel': ('Show formulas, pivots, data cleaning, and business conclusions.', 'Build a small dashboard from a messy dataset and document the decisions.'),
    'Git': ('Show collaborative version control and a repeatable development workflow.', 'Publish a project with meaningful commits, a README, and a pull-request example.'),
    'Java': ('Demonstrate object-oriented design, testing, and maintainable services.', 'Build or document one Java service with tests and a clear README.'),
    'JavaScript': ('Show interactive, maintainable front-end or Node.js work.', 'Publish a small feature with tests, error handling, and deployment notes.'),
    'Jira': ('Show how you manage work, risks, dependencies, and delivery visibility.', 'Create a sample board and explain how you would manage one delivery risk.'),
    'Manual testing': ('Demonstrate structured exploratory and regression testing.', 'Write a test plan with risk-based coverage and defect evidence.'),
    'Power BI': ('Turn business questions into a clear dashboard and recommendation.', 'Publish a dashboard walkthrough with a decision and measurable insight.'),
    'Product strategy': ('Connect customer problems, trade-offs, and business outcomes.', 'Write a one-page product case with assumptions, metrics, and prioritization.'),
    'Project management': ('Show scope, planning, communication, and risk ownership.', 'Prepare a delivery case study covering scope, risks, and outcomes.'),
    'Python': ('Demonstrate readable automation, analysis, or backend code.', 'Publish a tested project with setup instructions and one measurable result.'),
    'Requirements gathering': ('Convert stakeholder needs into clear, testable requirements.', 'Create a sample requirements brief with acceptance criteria.'),
    'Roadmapping': ('Explain sequencing, dependencies, and outcome-based prioritization.', 'Create a roadmap tied to user outcomes and success metrics.'),
    'Scrum': ('Show practical use of ceremonies, roles, and iterative delivery.', 'Describe one sprint cycle and the improvement you would make next.'),
    'Selenium': ('Demonstrate browser automation with stable, maintainable tests.', 'Build a small page-object test suite with readable failure output.'),
    'SQL': ('Show that you can query, validate, and explain data accurately.', 'Add a SQL case study with joins, aggregations, and a business conclusion.'),
    'Statistics': ('Use sound reasoning to interpret uncertainty and trends.', 'Explain one analysis with assumptions, method, and a decision.'),
    'Stakeholder management': ('Show how you align different priorities and communicate decisions.', 'Write a STAR story about resolving a stakeholder conflict.'),
    'Test cases': ('Show systematic coverage, traceability, and clear expected results.', 'Create a test matrix that maps risks to test cases.'),
    'User research': ('Show how customer evidence shaped a product decision.', 'Document interviews, themes, and the decision that followed.'),
}

SKILL_ALIASES = {
    'Agile': ('agile',),
    'Analytics': ('analytics', 'data analysis'),
    'API testing': ('api testing', 'api test', 'rest api'),
    'Excel': ('excel', 'microsoft excel'),
    'Git': ('git', 'github', 'gitlab'),
    'Java': ('java',),
    'JavaScript': ('javascript', 'js', 'node.js', 'node js'),
    'Jira': ('jira',),
    'Manual testing': ('manual testing', 'manual test'),
    'Power BI': ('power bi', 'powerbi'),
    'Product strategy': ('product strategy',),
    'Project management': ('project management', 'project manager'),
    'Python': ('python',),
    'Requirements gathering': ('requirements gathering', 'requirements analysis'),
    'Roadmapping': ('roadmapping', 'roadmap'),
    'Scrum': ('scrum',),
    'Selenium': ('selenium',),
    'SQL': ('sql', 'mysql', 'postgresql', 'postgres'),
    'Statistics': ('statistics', 'statistical analysis'),
    'Stakeholder management': ('stakeholder management', 'stakeholder communication'),
    'Test cases': ('test cases', 'test case', 'test scenarios'),
    'User research': ('user research', 'user interviews'),
}

ROLE_LIBRARY = (
    {
        'role': 'Business Analyst',
        'field': 'Business and product analytics',
        'skills': ('SQL', 'Excel', 'Power BI', 'Requirements gathering', 'Stakeholder management'),
        'summary': 'Translate business questions into requirements, analysis, and practical decisions.',
        'next_step': 'Build one case study showing the problem, analysis, recommendation, and measurable outcome.',
    },
    {
        'role': 'Data Analyst',
        'field': 'Data and reporting',
        'skills': ('SQL', 'Excel', 'Python', 'Power BI', 'Statistics'),
        'summary': 'Turn data into clear insights, dashboards, and recommendations for teams.',
        'next_step': 'Create a portfolio project with a clean dataset, dashboard, and written business recommendation.',
    },
    {
        'role': 'Product Manager',
        'field': 'Product management',
        'skills': ('Product strategy', 'User research', 'Analytics', 'Roadmapping', 'Stakeholder management'),
        'summary': 'Connect customer needs, business goals, and delivery teams around a product direction.',
        'next_step': 'Document a product decision with user evidence, trade-offs, success metrics, and a roadmap.',
    },
    {
        'role': 'Software Developer',
        'field': 'Software engineering',
        'skills': ('Python', 'Java', 'JavaScript', 'Git', 'SQL'),
        'summary': 'Design, build, test, and maintain reliable software features and services.',
        'next_step': 'Publish one production-style project with tests, documentation, and a clear deployment story.',
    },
    {
        'role': 'QA Analyst',
        'field': 'Quality engineering',
        'skills': ('Test cases', 'Manual testing', 'Selenium', 'SQL', 'Jira'),
        'summary': 'Protect product quality through structured testing, defect analysis, and release confidence.',
        'next_step': 'Create a test plan and defect report for a real or practice application, including risk-based coverage.',
    },
    {
        'role': 'Project Manager',
        'field': 'Project delivery',
        'skills': ('Project management', 'Agile', 'Scrum', 'Jira', 'Stakeholder management'),
        'summary': 'Coordinate people, scope, risks, and timelines to deliver work predictably.',
        'next_step': 'Show a delivery case study covering scope, risks, communication, and the result achieved.',
    },
)


def _clean(value, limit):
  return ' '.join(str(value or '').split())[:limit]


def _clean_long_text(value, limit):
  text = str(value or '').replace('\r\n', '\n').replace('\r', '\n')
  text = re.sub(r'[ \t]+\n', '\n', text)
  text = re.sub(r'\n{3,}', '\n\n', text)
  return text.strip()[:limit]


def _tokens(value):
  return set(re.findall(r'[a-z0-9+#]+', str(value or '').lower()))


def _normalised_text(value):
  return ' ' + re.sub(r'[^a-z0-9+#]+', ' ', str(value or '').lower()).strip() + ' '


def _extract_skills(value):
  text = _normalised_text(value)
  found = []
  for skill, aliases in SKILL_ALIASES.items():
    if any(' ' + alias + ' ' in text for alias in aliases):
      found.append(skill)
  return found


def _skill_list(value):
  raw_items = [
      _clean(item, 80)
      for item in re.split(r'[,;\n]+', str(value or ''))
      if _clean(item, 80)
  ]
  known = _extract_skills(value)
  return known + [item for item in raw_items if item.lower() not in {skill.lower() for skill in known}]

def _merge_skills(profile_skills, resume_text):
  merged = []
  seen = set()
  for skill in _skill_list(profile_skills) + _extract_skills(resume_text):
    normalized = skill.lower()
    if skill and normalized not in seen:
      merged.append(skill)
      seen.add(normalized)
  return ', '.join(merged)


def _matched_skills(current_skills, required_skills):
  detected = {skill.lower() for skill in _extract_skills(current_skills)}
  current_text = _normalised_text(current_skills)
  return [
      skill for skill in required_skills
      if skill.lower() in detected or ' ' + skill.lower() + ' ' in current_text
  ]


def _profile_context():
  conn = get_db_connection()
  try:
    with conn.cursor() as cursor:
      ensure_auth_schema(cursor)
      ensure_career_tools_schema(cursor)
      ensure_resume_analysis_schema(cursor)
      conn.commit()
      cursor.execute(
          """
          SELECT s.full_name, s.profile_type, s.branch, s.year,
                 fresher_profile.career_goal AS fresher_career_goal,
                 fresher_profile.target_role AS fresher_target_role,
                 fresher_profile.preferred_industry AS fresher_industry,
                 fresher_profile.preferred_location AS fresher_location,
                 professional_profile.current_job_title,
                 professional_profile.current_company,
                 professional_profile.key_skills,
                 professional_profile.target_field,
                 professional_profile.target_role AS professional_target_role,
                 professional_profile.preferred_location AS professional_location,
                 professional_profile.work_preference,
                 professional_profile.career_highlights
          FROM students AS s
          LEFT JOIN student_profile AS fresher_profile
              ON fresher_profile.student_id = s.student_id
             AND s.profile_type = 'fresher'
          LEFT JOIN professional_profile
              ON professional_profile.student_id = s.student_id
             AND s.profile_type = 'experienced'
          WHERE s.student_id = %s
          """,
          (session['student_id'],),
      )
      row = cursor.fetchone() or {}
      cursor.execute(
          """
          SELECT resume_text
          FROM resume_analysis
          WHERE student_id = %s
            AND resume_text IS NOT NULL
            AND resume_text <> ''
          ORDER BY created_at DESC, analysis_id DESC
          LIMIT 1
          """,
          (session['student_id'],),
      )
      latest_resume = cursor.fetchone() or {}
  finally:
    conn.close()

  experienced = row.get('profile_type') == 'experienced'
  resume_text = latest_resume.get('resume_text') or ''
  return {
      'full_name': row.get('full_name') or '',
      'profile_type': row.get('profile_type') or 'fresher',
      'current_job_title': row.get('current_job_title') or '',
      'current_company': row.get('current_company') or '',
      'skills': _merge_skills(row.get('key_skills') or row.get('branch') or '', resume_text),
      'resume_text': resume_text,
      'target_field': row.get('target_field') or row.get('fresher_industry') or '',
      'target_role': (
          row.get('professional_target_role') if experienced
          else row.get('fresher_target_role')
      ) or '',
      'preferred_location': (
          row.get('professional_location') if experienced
          else row.get('fresher_location')
      ) or '',
      'work_preference': row.get('work_preference') or '',
      'career_highlights': row.get('career_highlights') or '',
  }


def _skill_form_value(profile):
  provided = _clean(request.form.get('skills') or request.args.get('skills'), 1200)
  if not provided:
    return profile.get('skills', '')
  return _clean(_merge_skills(provided, profile.get('skills', '')), 1200)

def _role_score(target_role, role):
  target_tokens = _tokens(target_role)
  if not target_tokens:
    return 55
  role_tokens = _tokens(role['role'] + ' ' + role['field'])
  overlap = len(target_tokens & role_tokens)
  if target_role.strip().lower() == role['role'].lower():
    return 100
  return min(95, 45 + overlap * 18)


def _best_role(target_role):
  target_role = _clean(target_role, 120)
  if not target_role:
    return ROLE_LIBRARY[0]
  return max(ROLE_LIBRARY, key=lambda role: _role_score(target_role, role))


def _requirements(target_role, job_description):
  role = _best_role(target_role)
  extracted = _extract_skills(job_description)
  return role, extracted if len(extracted) >= 2 else list(role['skills'])


def _preference_score(location, work_preference, job_description):
  text = str(job_description or '').lower()
  signals = []
  if location:
    location_text = str(location).lower()
    if 'remote' in location_text:
      signals.append(100 if 'remote' in text else 35)
    else:
      location_token = _tokens(location_text)
      signals.append(100 if location_token and location_token & _tokens(text) else 45)
  if work_preference:
    preference = str(work_preference).lower()
    if preference == 'on-site':
      preference = 'on site'
    signals.append(100 if preference in text else 40)
  return round(sum(signals) / len(signals)) if signals else None


def _custom_job_fit(target_role, skills, job_description, location='', work_preference=''):
  if not job_description:
    return None
  role, required = _requirements(target_role, job_description)
  matched = _matched_skills(skills, required)
  missing = [skill for skill in required if skill not in matched]
  skill_score = round(100 * len(matched) / len(required)) if required else 0
  title_tokens = _tokens(target_role)
  description_tokens = _tokens(job_description)
  title_overlap = len(title_tokens & description_tokens) if title_tokens else 0
  title_score = min(100, 55 + title_overlap * 15) if title_tokens else 60
  preference_score = _preference_score(location, work_preference, job_description)
  if preference_score is None:
    match_score = round(0.8 * skill_score + 0.2 * title_score)
  else:
    match_score = round(0.7 * skill_score + 0.15 * title_score + 0.15 * preference_score)
  return {
      'role': _clean(target_role, 120) or role['role'],
      'field': role['field'],
      'match_score': match_score,
      'skill_score': skill_score,
      'title_score': title_score,
      'preference_score': preference_score,
      'required_skills': required,
      'matched_skills': matched,
      'missing_skills': missing,
      'summary': 'A job-description fit report based on recognisable requirements, preferences, and the skills in your profile.',
      'next_step': 'Use the missing skills as a checklist, then tailor your resume with truthful evidence for each matched requirement.',
  }


def _rank_roles(target_role, skills, job_description=''):
  ranked = []
  for role in ROLE_LIBRARY:
    required = _extract_skills(job_description) if job_description else list(role['skills'])
    if len(required) < 2:
      required = list(role['skills'])
    matched = _matched_skills(skills, required)
    missing = [skill for skill in required if skill not in matched]
    skill_score = round(100 * len(matched) / len(required)) if required else 0
    role_score = _role_score(target_role, role)
    score = round(0.7 * skill_score + 0.3 * role_score)
    ranked.append({
        **role,
        'match_score': score,
        'skill_score': skill_score,
        'role_score': role_score,
        'required_skills': required,
        'matched_skills': matched,
        'missing_skills': missing,
    })
  return sorted(ranked, key=lambda item: (-item['match_score'], item['role']))[:5]


def _gap_report(target_role, skills, job_description=''):
  role, required = _requirements(target_role, job_description)
  matched = _matched_skills(skills, required)
  missing = [skill for skill in required if skill not in matched]
  action_plan = []
  for skill in missing:
    detail = SKILL_DETAILS.get(skill, (
        'Add a truthful example that shows how you used this skill.',
        'Create one small work sample and connect it to a measurable outcome.',
    ))
    action_plan.append({'skill': skill, 'why': detail[0], 'action': detail[1]})
  return {
      'role': _clean(target_role, 120) or role['role'],
      'field': role['field'],
      'summary': role['summary'] if not job_description else 'This report compares your profile with the requirements detected in the pasted job description.',
      'readiness': round(100 * len(matched) / len(required)) if required else 0,
      'required_skills': required,
      'matched_skills': matched,
      'missing_skills': missing,
      'action_plan': action_plan,
      'next_step': role['next_step'],
  }


def _content_lines(value):
  """Return useful resume-like lines without trying to rewrite the source text."""
  lines = []
  for item in re.split(r'\r?\n+|(?<=[.!?])\s+', str(value or '')):
    cleaned = _clean(item, 420).lstrip('-* ').strip()
    if len(cleaned.split()) >= 5:
      lines.append(cleaned)
  return lines[:24]


def _has_resume_heading(text, headings):
  normalized_headings = {re.sub(r'\s+', ' ', heading.lower()).strip() for heading in headings}
  for line in str(text or '').splitlines():
    normalized = re.sub(r'[^a-z0-9+#& ]+', ' ', line.lower())
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    if normalized in normalized_headings:
      return True
  return False


def _tool_form(profile, fields, overrides=None):
  defaults = {
      'current_role': profile.get('current_job_title', ''),
      'current_company': profile.get('current_company', ''),
      'target_role': profile.get('target_role', ''),
      'target_field': profile.get('target_field', ''),
      'skills': profile.get('skills', ''),
      'highlights': profile.get('career_highlights', ''),
      'target_company': '',
      'job_description': '',
      'resume_text': profile.get('resume_text') or profile.get('career_highlights', ''),
      'recruiter_name': '',
      'company': '',
  }
  overrides = overrides or {}
  form = {
      field: (_clean_long_text if field in {'resume_text', 'job_description'} else _clean)(
          request.form.get(field) or overrides.get(field) or defaults.get(field, ''),
          8000 if field in {'resume_text', 'job_description'} else 1600,
      )
      for field in fields
  }
  if 'resume_text' not in form:
    form['resume_text'] = _clean_long_text(
        request.form.get('resume_text') or overrides.get('resume_text') or defaults['resume_text'],
        8000,
    )
  return form


def _evidence_text(form, *fields):
  parts = [str(form.get(field) or '').strip() for field in fields if str(form.get(field) or '').strip()]
  resume_text = str(form.get('resume_text') or '').strip()
  if resume_text and resume_text not in parts:
    parts.append(resume_text)
  return '\n'.join(parts)


def _health_report(form):
  text = form.get('resume_text', '')
  lower = text.lower()
  words = len(text.split())
  sections = {
      'Contact details': bool(re.search(r'@|linkedin|\+?\d[\d\s().-]{7,}', text, re.I)),
      'Professional summary': _has_resume_heading(text, ('summary', 'professional summary', 'profile', 'professional profile', 'objective', 'about me')),
      'Work experience': _has_resume_heading(text, ('experience', 'work experience', 'professional experience', 'employment', 'work history', 'career history')),
      'Skills': _has_resume_heading(text, ('skills', 'technical skills', 'core skills', 'technologies', 'competencies', 'expertise')),
      'Education': _has_resume_heading(text, ('education', 'academic background', 'academic qualifications')),
      'Projects or achievements': _has_resume_heading(text, ('projects', 'selected projects', 'achievements', 'key achievements', 'awards', 'impact')),
  }
  metrics = len(re.findall(
      r'(?<!\d)(?:\d+(?:\.\d+)?\s*%|\d[\d,]*\+|[$₹€£]\s?\d[\d,]*)(?!\d)',
      text,
  ))
  action_verbs = len(re.findall(r'\b(led|built|created|improved|delivered|managed|launched|reduced|increased|automated|owned|developed|optimized|coordinated|designed)\b', lower))
  if not sections['Projects or achievements'] and metrics and action_verbs >= 2:
    sections['Projects or achievements'] = True
  section_score = round(100 * sum(sections.values()) / len(sections)) if sections else 0
  evidence_score = min(100, metrics * 20 + action_verbs * 5)
  length_score = 100 if 350 <= words <= 900 else 70 if 180 <= words <= 1200 else 35
  target_score = 100 if form.get('target_role') and form.get('job_description') else 70 if form.get('target_role') else 40
  score = round(0.35 * section_score + 0.3 * evidence_score + 0.15 * length_score + 0.2 * target_score)
  checks = []
  for label, present in sections.items():
    checks.append({
        'heading': label,
        'body': 'Present in the supplied text.' if present else 'Not detected; add a clear section so recruiters and ATS can find it.',
        'status': 'good' if present else 'needs-work',
    })
  if form.get('target_role') and form.get('job_description'):
    target_body = 'A role and job description are available for tailoring.'
    target_status = 'good'
  elif form.get('target_role'):
    target_body = f'Target role detected: {form["target_role"]}. Add a job description for sharper alignment.'
    target_status = 'needs-work'
  else:
    target_body = 'Add a target role and job description for a sharper diagnostic.'
    target_status = 'needs-work'
  checks.extend([
      {'heading': 'Measured outcomes', 'body': f'{metrics} quantified result(s) detected.' if metrics else 'Add truthful numbers, scale, time, cost, volume, or quality outcomes.', 'status': 'good' if metrics else 'needs-work'},
      {'heading': 'Target alignment', 'body': target_body, 'status': target_status},
  ])
  return {
      'score': score,
      'summary': 'Your resume has a clear starting point. Fix the highest-signal gaps first, then rerun the check.',
      'metrics': [
          {'label': 'Section coverage', 'value': f'{section_score}%'},
          {'label': 'Evidence signals', 'value': f'{evidence_score}%'},
          {'label': 'Quantified results', 'value': str(metrics)},
          {'label': 'Word count', 'value': str(words)},
      ],
      'sections': [
          {'heading': 'Diagnostic checks', 'items': checks},
          {'heading': 'Priority fixes', 'items': [
              'Add a quantified outcome to the strongest responsibility bullet.' if not metrics else 'Keep the strongest metrics close to the action that produced them.',
              'Make the target role visible in the summary and experience wording.' if not form.get('target_role') else f'Use the language of {form["target_role"]} only where your evidence supports it.',
              'Keep section headings conventional so both recruiters and ATS can scan them.',
          ]},
      ],
      'notice': 'This is a local diagnostic, not a hiring prediction. Verify every recommendation against your real experience.',
  }


def _positioning_report(form):
  current = form.get('current_role') or 'your current role'
  target = form.get('target_role') or 'your next role'
  field = form.get('target_field') or 'the target field'
  company = form.get('target_company')
  evidence = _evidence_text(form, 'highlights', 'skills')
  skills = _skill_list(evidence)
  strengths = ', '.join(skills[:4]) if skills else 'transferable delivery and problem-solving experience'
  statement = f'{current} with evidence in {strengths}, positioning for {target} in {field}.'
  if company:
    statement += f' For {company}, lead with the business outcomes you can repeat in that environment.'
  highlights = _content_lines(evidence)
  return {
      'score': min(100, 55 + len(skills) * 8 + (15 if form.get('target_role') else 0) + (10 if form.get('target_field') else 0)),
      'summary': 'A strong positioning statement connects your proven value to the work you want next; it does not hide your career history.',
      'metrics': [
          {'label': 'Current anchor', 'value': current},
          {'label': 'Target direction', 'value': target},
          {'label': 'Transferable strengths', 'value': str(len(skills))},
      ],
      'sections': [
          {'heading': 'Positioning statement', 'body': statement},
          {'heading': 'Lead with these proof points', 'items': highlights[:4] or ['Add two or three outcomes that show ownership, not only responsibilities.']},
          {'heading': 'Avoid', 'items': ['A generic objective that could describe anyone.', 'Listing every task instead of selecting evidence tied to the target role.', 'Claiming target-field expertise before building visible proof.']},
      ],
      'notice': 'Use this language as a starting point. Replace broad phrases with facts you can explain in an interview.',
  }


def _switch_report(form):
  target_role = form.get('target_role') or form.get('target_field') or ''
  role, required = _requirements(target_role, '')
  current_skills = _evidence_text(form, 'skills', 'highlights')
  matched = _matched_skills(current_skills, required)
  missing = [skill for skill in required if skill not in matched]
  target_field = form.get('target_field') or role['field']
  actions = []
  for skill in missing[:4]:
    detail = SKILL_DETAILS.get(skill, ('Show a truthful example of this capability.', 'Create one small work sample and document the result.'))
    actions.append({'heading': f'Build evidence: {skill}', 'body': detail[1]})
  actions.extend([
      {'heading': 'Reframe existing experience', 'body': f'Select two examples from {form.get("current_role") or "your current role"} that show outcomes transferable to {target_role or "the target role"}.'},
      {'heading': 'Test the direction', 'body': f'Have one conversation or complete one realistic work sample in {target_field} before making a full resume change.'},
  ])
  readiness = round(100 * len(matched) / len(required)) if required else 35
  return {
      'score': readiness,
      'summary': f'Your switch plan treats {form.get("current_role") or "your current experience"} as an asset while making the missing proof visible for {target_role or "the new direction"}.',
      'metrics': [
          {'label': 'Transferable match', 'value': f'{readiness}%'},
          {'label': 'Skills already visible', 'value': str(len(matched))},
          {'label': 'Skills to prove', 'value': str(len(missing))},
      ],
      'sections': [
          {'heading': 'Bridge plan', 'items': actions},
          {'heading': 'Resume repositioning', 'items': [
              f'Lead with outcomes that connect {form.get("current_role") or "your current role"} to {target_role or "the target role"}.',
              'Move transferable skills and relevant projects above low-value task lists.',
              'Add a short transition line only if it explains the business problem you want to solve next.',
          ]},
      ],
      'notice': 'A career switch is more credible when every new claim has a project, result, course, or work example behind it.',
  }


def _achievement_report(form):
  source = form.get('resume_text') or form.get('highlights')
  lines = _content_lines(source)
  action_pattern = r'\b(led|built|created|improved|delivered|managed|launched|reduced|increased|automated|owned|developed|optimized|coordinated|designed|implemented)\b'
  items = []
  for line in lines[:8]:
    has_action = bool(re.search(action_pattern, line, re.I))
    has_metric = bool(re.search(r'(?<!\d)(?:\d{1,3}(?:,\d{3})*\+?|\d+(?:\.\d+)?%|[$₹€£]\s?\d+)', line))
    signal = 'Strong evidence' if has_action and has_metric else 'Add outcome detail' if has_action else 'Rewrite around ownership'
    edit = 'Keep this bullet and make the result easy to scan.' if has_action and has_metric else 'Add a truthful metric, scale, time, or quality result after the action.' if has_action else 'Start with the decision or action you personally owned, then add the outcome.'
    items.append({'heading': signal, 'body': f'Source: {line} | Next edit: {edit}'})
  return {
      'score': min(100, len(items) * 10 + sum(bool(re.search(r'\d', item['body'])) for item in items) * 8),
      'summary': 'The strongest resume bullets show what you owned, what changed, and how the change can be verified.',
      'metrics': [
          {'label': 'Bullets reviewed', 'value': str(len(items))},
          {'label': 'Action-led signals', 'value': str(sum(bool(re.search(action_pattern, line, re.I)) for line in lines))},
          {'label': 'Metric signals', 'value': str(sum(bool(re.search(r'\d', line)) for line in lines))},
      ],
      'sections': [
          {'heading': 'Extracted evidence', 'items': items or [{'heading': 'Paste experience bullets', 'body': 'Add the text from your experience section to identify achievements.'}]},
          {'heading': 'Achievement formula', 'body': 'Action you owned + problem or scope + measurable result + why it mattered.'},
      ],
      'notice': 'The tool never invents achievements. It only points to evidence and the fact you still need to verify or add.',
  }


def _ats_report(form):
  job_text = form.get('job_description', '')
  resume_text = ' '.join((form.get('resume_text', ''), form.get('skills', '')))
  role, required_skills = _requirements(form.get('target_role', ''), job_text)
  resume_lower = _normalised_text(resume_text)
  skill_keywords = list(dict.fromkeys(required_skills + _extract_skills(job_text)))
  stop_words = {'about', 'their', 'there', 'which', 'where', 'these', 'those', 'with', 'from', 'into', 'will', 'have', 'your', 'that', 'this', 'must', 'work', 'team', 'role'}
  word_keywords = []
  for word in re.findall(r'[a-z][a-z0-9+#.-]{4,}', job_text.lower()):
    word = word.strip('.')
    if word not in stop_words and word not in word_keywords:
      word_keywords.append(word)
  keywords = list(dict.fromkeys(skill_keywords + word_keywords[:12]))
  matched = [keyword for keyword in keywords if ' ' + keyword.lower() + ' ' in resume_lower or keyword.lower() in resume_lower]
  missing = [keyword for keyword in keywords if keyword not in matched]
  score = round(100 * len(matched) / len(keywords)) if keywords else 0
  return {
      'score': score,
      'summary': f'Keyword alignment is {score}%. Use the missing terms only when they describe real work you can prove.',
      'metrics': [
          {'label': 'Keywords checked', 'value': str(len(keywords))},
          {'label': 'Visible in resume', 'value': str(len(matched))},
          {'label': 'Needs evidence', 'value': str(len(missing))},
      ],
      'sections': [
          {'heading': 'Already visible', 'items': matched or ['No matching keywords detected yet.']},
          {'heading': 'Add or prove next', 'items': missing or ['No major keyword gaps detected from this job post.']},
          {'heading': 'Placement guidance', 'items': [f'Use {form.get("target_role") or role["role"]} in the headline or summary when it is truthful.', 'Place the most important matched skills near the relevant achievement, not only in a keyword list.', 'Do not paste the job description into the resume.']},
      ],
      'notice': 'ATS alignment is a visibility check. It does not replace readable writing or evidence of results.',
  }


def _linkedin_report(form):
  current = form.get('current_role') or 'Working professional'
  target = form.get('target_role') or 'open to the next opportunity'
  field = form.get('target_field') or 'your field'
  evidence = _evidence_text(form, 'skills', 'highlights')
  skills = _skill_list(evidence)
  skill_line = ', '.join(skills[:5]) or 'delivery, problem-solving, and stakeholder collaboration'
  highlights = _content_lines(evidence)
  about = f'I am a {current} focused on {skill_line}. I am exploring {target} opportunities in {field}, where I can apply proven experience to meaningful business outcomes.'
  if highlights:
    about += f' Recent work includes: {highlights[0]}'
  return {
      'score': min(100, 45 + len(skills) * 9 + (15 if form.get('target_role') else 0)),
      'summary': 'Your LinkedIn profile should mirror the target direction while keeping the proof anchored in work you have actually done.',
      'metrics': [
          {'label': 'Headline length', 'value': str(len(f'{current} | {target} | {skill_line}'))},
          {'label': 'Skills to feature', 'value': str(min(5, len(skills)))},
          {'label': 'Proof points', 'value': str(len(highlights))},
      ],
      'sections': [
          {'heading': 'Suggested headline', 'body': f'{current} | {target} | {skill_line}'[:220]},
          {'heading': 'Suggested About section', 'body': about},
          {'heading': 'Profile actions', 'items': ['Add three Featured items that prove your target direction.', 'Ask for recommendations that describe outcomes and collaboration, not only personality.', 'Use the same target role language as the resume so recruiters see one coherent story.']},
      ],
      'notice': 'Review the draft for accuracy and add links, examples, and metrics before publishing.',
  }


def _recruiter_message_report(form):
  recruiter = form.get('recruiter_name') or 'Hi there'
  company = form.get('company') or 'your team'
  role = form.get('target_role') or 'the opportunity'
  proof = _content_lines(_evidence_text(form, 'highlights'))
  proof_line = proof[0] if proof else 'I bring transferable experience and would be glad to share relevant examples.'
  message = f'{recruiter}, I am interested in the {role} opportunity at {company}. {proof_line} I am exploring roles where I can apply that experience to the team\'s goals. If the role is still active, would you be open to a brief conversation about the most important outcomes for the person joining? I can share a focused resume and relevant work examples.'
  return {
      'score': 75 if form.get('company') and form.get('target_role') else 45,
      'summary': 'A good recruiter message is short, specific, evidence-based, and easy to answer.',
      'metrics': [
          {'label': 'Message length', 'value': f'{len(message.split())} words'},
          {'label': 'Role named', 'value': 'Yes' if form.get('target_role') else 'Add role'},
          {'label': 'Proof included', 'value': 'Yes' if proof else 'Add proof'},
      ],
      'sections': [
          {'heading': 'Copy-ready message', 'body': message},
          {'heading': 'Follow-up rule', 'body': 'If there is no reply, send one useful follow-up after five to seven business days. Add a new relevant proof point instead of repeating the first message.'},
      ],
      'notice': 'Personalize the greeting and verify the opportunity is still active before sending.',
  }


def _leadership_report(form):
  source = form.get('resume_text') or form.get('highlights')
  text = source.lower()
  signals = {
      'People leadership': bool(re.search(r'\b(mentored|coached|managed|hired|led a team|direct reports)\b', text)),
      'Ownership': bool(re.search(r'\b(owned|accountable|drove|spearheaded|led|launched)\b', text)),
      'Influence': bool(re.search(r'\b(stakeholder|cross-functional|partnered|aligned|negotiated)\b', text)),
      'Decision-making': bool(re.search(r'\b(strategy|prioritized|decided|roadmap|budget|risk|trade-off)\b', text)),
      'Scale or outcomes': bool(re.search(r'\d|%|\$|₹|€|£', text)),
  }
  score = round(100 * sum(signals.values()) / len(signals))
  checks = [{'heading': label, 'body': 'Signal detected in the supplied text.' if present else 'Add a truthful example that shows this leadership dimension.', 'status': 'good' if present else 'needs-work'} for label, present in signals.items()]
  return {
      'score': score,
      'summary': 'Promotion-ready resumes show the scope of decisions and influence, not only a longer list of tasks.',
      'metrics': [
          {'label': 'Leadership signals', 'value': f'{score}%'},
          {'label': 'Scope dimensions', 'value': f'{sum(signals.values())}/{len(signals)}'},
          {'label': 'Target level', 'value': form.get('target_role') or 'Next-level role'},
      ],
      'sections': [
          {'heading': 'Leadership diagnostic', 'items': checks},
          {'heading': 'Upgrade one bullet', 'body': 'Context or scope + decision you owned + people or stakeholder movement + measurable business result.'},
      ],
      'notice': 'Leadership is not only people management. Show influence, judgment, scope, and outcomes where they are real.',
  }


def _story_report(form):
  current = form.get('current_role') or 'my current role'
  target = form.get('target_role') or 'the next role'
  field = form.get('target_field') or 'the target field'
  highlights = _content_lines(_evidence_text(form, 'highlights'))
  proof = highlights[0] if highlights else 'I have built experience solving problems, delivering work, and collaborating with stakeholders.'
  thirty_seconds = f'I currently work as {current}, where I have built experience through {proof.lower()} I am now targeting {target} in {field} because I want to apply those strengths to a broader set of problems. I am building the remaining proof deliberately through relevant projects, learning, and conversations.'
  return {
      'score': 80 if form.get('current_role') and form.get('target_role') and highlights else 50,
      'summary': 'The story connects past proof, a reason for the move, and a credible next step without apologizing for the transition.',
      'metrics': [
          {'label': 'Current anchor', 'value': current},
          {'label': 'Next direction', 'value': target},
          {'label': 'Proof points', 'value': str(len(highlights))},
      ],
      'sections': [
          {'heading': '30-second version', 'body': thirty_seconds},
          {'heading': 'Story structure', 'items': [
              {'heading': 'Past', 'body': f'What you learned and delivered in {current}.'},
              {'heading': 'Proof', 'body': proof},
              {'heading': 'Bridge', 'body': f'Why those strengths transfer to {target} in {field}.'},
              {'heading': 'Future', 'body': 'What you want to contribute and what proof you are building next.'},
          ]},
      ],
      'notice': 'Keep the story conversational and use it to open a discussion; do not memorize it word for word.',
  }


def _run_professional_tool(slug, form):
  runners = {
      'resume-health': _health_report,
      'career-positioning': _positioning_report,
      'career-switch-planner': _switch_report,
      'achievement-extractor': _achievement_report,
      'ats-optimizer': _ats_report,
      'linkedin-optimizer': _linkedin_report,
      'recruiter-message': _recruiter_message_report,
      'promotion-leadership': _leadership_report,
      'career-story': _story_report,
  }
  return runners[slug](form)


def _tailoring_summary(form):
  required = _extract_skills(form.get('job_description'))
  available = _extract_skills(
      ' '.join((form.get('skills'), form.get('highlights'), form.get('resume_text'), form.get('current_job_title')))
  )
  matched = [skill for skill in required if skill in available]
  missing = [skill for skill in required if skill not in matched]
  return {
      'required': required,
      'matched': matched,
      'missing': missing,
      'coverage': round(100 * len(matched) / len(required)) if required else None,
  }


def _cover_letter(form):
  name = form['full_name'] or 'Your Name'
  current_role = form['current_job_title'] or 'a professional with relevant experience'
  current_company = form['current_company'] or 'my current organization'
  role = form['target_role']
  company = form['company']
  highlights = form['highlights'] or form.get('resume_text') or 'I have built practical experience solving problems, collaborating with stakeholders, and delivering reliable outcomes.'
  skills = ', '.join(_extract_skills(form['skills'])[:6] or _skill_list(form['skills'])[:6])
  tailoring = _tailoring_summary(form)
  skill_sentence = f' My strongest relevant skills include {skills}.' if skills else ''
  requirement_sentence = ''
  if tailoring['matched']:
    requirement_sentence = (
        f" The requirements that align most closely with my background include "
        f"{', '.join(tailoring['matched'][:4])}."
    )
  return (
      f'Dear Hiring Manager,\n\n'
      f'I am writing to apply for the {role} position at {company}. '
      f'In my current role as {current_role} at {current_company}, I have developed '
      f'experience that I believe can contribute to your team.{skill_sentence}{requirement_sentence}\n\n'
      f'{highlights}\n\n'
      f'I am interested in {company} because this opportunity matches the direction '
      f'I want to take next in my career. I would welcome the opportunity to discuss '
      f'how my experience can support your goals.\n\n'
      f'Thank you for your time and consideration.\n\n'
      f'Sincerely,\n{name}'
  )


def _parse_date(value, label):
  value = _clean(value, 10)
  if not value:
    return None, None
  try:
    return datetime.strptime(value, '%Y-%m-%d').date(), None
  except ValueError:
    return None, f'Choose a valid {label}.'


def _application_form(form):
  return {
      'company_name': _clean(form.get('company_name'), 150),
      'job_title': _clean(form.get('job_title'), 150),
      'status': _clean(form.get('status') or 'Saved', 30),
      'priority': _clean(form.get('priority') or 'Medium', 20),
      'location': _clean(form.get('location'), 150),
      'application_url': _clean(form.get('application_url'), 500),
      'source': _clean(form.get('source'), 120),
      'job_description': _clean(form.get('job_description'), 8000),
      'next_action_date': _clean(form.get('next_action_date'), 10),
      'next_action': _clean(form.get('next_action'), 500),
      'last_contacted': _clean(form.get('last_contacted'), 10),
      'notes': _clean(form.get('notes'), 2000),
  }


def _validate_application(form, profile):
  values = _application_form(form)
  if not values['company_name'] or not values['job_title']:
    return values, None, 'Company and job title are required.'
  if values['status'] not in APPLICATION_STATUSES:
    return values, None, 'Choose a valid application status.'
  if values['priority'] not in APPLICATION_PRIORITIES:
    return values, None, 'Choose a valid application priority.'
  if values['application_url'] and not re.fullmatch(r'https?://[^\s]+', values['application_url'], re.IGNORECASE):
    return values, None, 'Application URL must start with http:// or https://.'
  next_date, error = _parse_date(values['next_action_date'], 'follow-up date')
  if error:
    return values, None, error
  last_contacted, error = _parse_date(values['last_contacted'], 'contact date')
  if error:
    return values, None, error
  fit = _custom_job_fit(values['job_title'], profile.get('skills', ''), values['job_description'], values['location'], '')
  payload = {
      **values,
      'next_action_date': next_date,
      'last_contacted': last_contacted,
      'match_score': fit['match_score'] if fit else None,
  }
  return values, payload, None


def _decorate_application(row):
  item = dict(row)
  follow_up = item.get('next_action_date')
  if follow_up:
    if follow_up < date.today():
      item['follow_up_state'] = 'overdue'
    elif follow_up == date.today():
      item['follow_up_state'] = 'today'
    else:
      item['follow_up_state'] = 'upcoming'
    item['next_action_date_label'] = follow_up.strftime('%d %b %Y')
  else:
    item['follow_up_state'] = 'none'
    item['next_action_date_label'] = ''
  if item.get('last_contacted'):
    item['last_contacted_label'] = item['last_contacted'].strftime('%d %b %Y')
  else:
    item['last_contacted_label'] = ''
  return item


def _application_rows():
  conn = get_db_connection()
  try:
    with conn.cursor() as cursor:
      ensure_career_tools_schema(cursor)
      conn.commit()
      cursor.execute(
          """
          SELECT application_id, company_name, job_title, status, priority,
                 location, application_url, source, job_description,
                 next_action_date, next_action, last_contacted, match_score,
                 notes, created_at, updated_at
          FROM job_applications
          WHERE student_id = %s
          ORDER BY COALESCE(next_action_date, '9999-12-31'), updated_at DESC
          """,
          (session['student_id'],),
      )
      return [_decorate_application(row) for row in (cursor.fetchall() or [])]
  finally:
    conn.close()


def _tracker_snapshot(search='', status='', priority=''):
  all_rows = _application_rows()
  query = _clean(search, 100).lower()
  filtered = [
      row for row in all_rows
      if (not status or row['status'] == status)
      and (not priority or row['priority'] == priority)
      and (not query or query in ' '.join(str(row.get(key) or '') for key in ('company_name', 'job_title', 'location', 'notes')).lower())
  ]
  metrics = {
      'total': len(all_rows),
      'active': sum(row['status'] not in ('Rejected', 'Withdrawn', 'Offer') for row in all_rows),
      'interviews': sum(row['status'] == 'Interview' for row in all_rows),
      'offers': sum(row['status'] == 'Offer' for row in all_rows),
      'follow_ups': sum(row['follow_up_state'] in ('overdue', 'today') for row in all_rows),
  }
  return filtered, metrics


def _professional_catalog(context=None):
  context = {
      key: _clean((context or {}).get(key), 160)
      for key in ('target_role', 'target_field', 'target_company')
      if _clean((context or {}).get(key), 160)
  }
  catalog = []
  for item in PROFESSIONAL_TOOL_CATALOG:
    tool = dict(item)
    if tool.get('endpoint'):
      tool['url'] = url_for(f"career_tools.{tool['endpoint']}", **context)
    else:
      tool['url'] = url_for('career_tools.professional_tool', tool_slug=tool['slug'], **context)
    catalog.append(tool)
  return catalog


@career_tools.route('/')
@login_required
def tools_home():
  return render_template(
      'tools/index.html',
      active_tool='home',
      professional_catalog=_professional_catalog(),
      professional_suite=False,
  )


@career_tools.route('/working-professional')
@login_required
def professional_suite():
  context = {
      key: request.args.get(key, '')
      for key in ('target_role', 'target_field', 'target_company')
  }
  return render_template(
      'tools/index.html',
      active_tool='professional-suite',
      professional_catalog=_professional_catalog(context),
      professional_suite=True,
  )


@career_tools.route('/professional/<tool_slug>', methods=['GET', 'POST'])
@login_required
def professional_tool(tool_slug):
  config = PROFESSIONAL_TOOL_CONFIG.get(tool_slug)
  if not config:
    return redirect(url_for('career_tools.professional_suite'))
  profile = _profile_context()
  form = _tool_form(profile, config['fields'], request.args)
  result = _run_professional_tool(tool_slug, form) if request.method == 'POST' else None
  field_meta = {
      field: {
          'label': PROFESSIONAL_FIELD_LABELS[field][0],
          'placeholder': PROFESSIONAL_FIELD_LABELS[field][1],
          'kind': PROFESSIONAL_FIELD_LABELS[field][2],
      }
      for field in config['fields']
  }
  return render_template(
      'tools/professional_tool.html',
      active_tool=tool_slug,
      config=config,
      form=form,
      field_meta=field_meta,
      result=result,
      profile=profile,
      professional_catalog=_professional_catalog(request.args),
  )


@career_tools.route('/job-matcher', methods=['GET', 'POST'])
@login_required
def job_matcher():
  profile = _profile_context()
  form = {
      'target_role': _clean(request.form.get('target_role') or request.args.get('target_role') or profile['target_role'], 120),
      'company': _clean(request.form.get('company') or request.args.get('target_company') or request.args.get('company'), 160),
      'skills': _skill_form_value(profile),
      'location': _clean(request.form.get('location') or profile['preferred_location'], 150),
      'work_preference': _clean(request.form.get('work_preference') or profile['work_preference'], 30),
      'job_description': _clean(request.form.get('job_description'), 8000),
  }
  has_input = any(form.values())
  matches = _rank_roles(form['target_role'], form['skills'], form['job_description']) if has_input else []
  custom_fit = _custom_job_fit(form['target_role'], form['skills'], form['job_description'], form['location'], form['work_preference'])
  ai_insight = None
  if request.method == 'POST' and has_input:
    with ai_feature_context('job_matcher', session.get('student_id')):
      ai_insight = job_match_insights(profile, form, custom_fit, matches)
  return render_template(
      'tools/job_matcher.html', profile=profile, form=form,
      matches=matches, custom_fit=custom_fit, ai_insight=ai_insight,
      active_tool='job-matcher',
  )


@career_tools.route('/skill-gap', methods=['GET', 'POST'])
@login_required
def skill_gap():
  profile = _profile_context()
  form = {
      'target_role': _clean(request.form.get('target_role') or request.args.get('target_role') or profile['target_role'], 120),
      'skills': _skill_form_value(profile),
      'job_description': _clean(request.form.get('job_description'), 8000),
  }
  gap = _gap_report(form['target_role'], form['skills'], form['job_description'])
  ai_insight = None
  if request.method == 'POST':
    with ai_feature_context('skill_gap', session.get('student_id')):
      ai_insight = skill_gap_insights(profile, form, gap)
  return render_template(
      'tools/skill_gap.html', profile=profile, form=form,
      gap=gap, ai_insight=ai_insight, active_tool='skill-gap',
  )


@career_tools.route('/cover-letter', methods=['GET', 'POST'])
@login_required
def cover_letter():
  profile = _profile_context()
  form = {
      'company': _clean(request.form.get('company') or request.args.get('target_company') or request.args.get('company'), 150),
      'target_role': _clean(request.form.get('target_role') or request.args.get('target_role') or profile['target_role'], 150),
      'skills': _skill_form_value(profile),
      'highlights': _clean(request.form.get('highlights') or profile['career_highlights'], 1200),
      'job_description': _clean(request.form.get('job_description'), 4000),
      'full_name': profile['full_name'],
      'current_job_title': profile['current_job_title'],
      'current_company': profile['current_company'],
      'resume_text': profile['resume_text'],
  }
  error = None
  letter = None
  letter_source = None
  ai_verification = []
  tailoring = _tailoring_summary(form)
  if request.method == 'POST':
    if not form['company'] or not form['target_role']:
      error = 'Add both the company name and target role to create a draft.'
    else:
      with ai_feature_context('cover_letter', session.get('student_id')):
        ai_letter = cover_letter_draft(form, tailoring)
      if ai_letter:
        letter = ai_letter['letter']
        ai_verification = ai_letter['verification_points']
        letter_source = 'ai'
      else:
        letter = _cover_letter(form)
        letter_source = 'template'
      if request.form.get('action') == 'download':
        filename = re.sub(r'[^a-z0-9]+', '-', form['target_role'].lower()).strip('-') or 'cover-letter'
        return Response(
            letter,
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment; filename={filename}-cover-letter.txt'},
        )
  return render_template(
      'tools/cover_letter.html', profile=profile, form=form,
      letter=letter, letter_source=letter_source, ai_verification=ai_verification,
      tailoring=tailoring, error=error, active_tool='cover-letter',
  )


@career_tools.route('/application-tracker', methods=['GET', 'POST'])
@login_required
def application_tracker():
  error = None
  if request.method == 'POST':
    action = request.form.get('action', 'add')
    conn = None
    try:
      conn = get_db_connection()
      with conn.cursor() as cursor:
        ensure_career_tools_schema(cursor)
        if action in ('add', 'update'):
          profile = _profile_context()
          values, payload, error = _validate_application(request.form, profile)
          if not error:
            if action == 'add':
              cursor.execute(
                  """
                  INSERT INTO job_applications (
                      student_id, company_name, job_title, status, priority,
                      location, application_url, source, job_description,
                      next_action_date, next_action, last_contacted,
                      match_score, notes
                  ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                  """,
                  (
                      session['student_id'], payload['company_name'], payload['job_title'],
                      payload['status'], payload['priority'], payload['location'] or None,
                      payload['application_url'] or None, payload['source'] or None,
                      payload['job_description'] or None, payload['next_action_date'],
                      payload['next_action'] or None, payload['last_contacted'],
                      payload['match_score'], payload['notes'] or None,
                  ),
              )
            else:
              application_id = int(request.form.get('application_id', '0'))
              cursor.execute(
                  """
                  UPDATE job_applications
                  SET company_name=%s, job_title=%s, status=%s, priority=%s,
                      location=%s, application_url=%s, source=%s,
                      job_description=%s, next_action_date=%s, next_action=%s,
                      last_contacted=%s, match_score=%s, notes=%s
                  WHERE application_id=%s AND student_id=%s
                  """,
                  (
                      payload['company_name'], payload['job_title'], payload['status'],
                      payload['priority'], payload['location'] or None,
                      payload['application_url'] or None, payload['source'] or None,
                      payload['job_description'] or None, payload['next_action_date'],
                      payload['next_action'] or None, payload['last_contacted'],
                      payload['match_score'], payload['notes'] or None,
                      application_id, session['student_id'],
                  ),
              )
        elif action == 'status':
          application_id = int(request.form.get('application_id', '0'))
          status = _clean(request.form.get('status'), 30)
          if status not in APPLICATION_STATUSES:
            error = 'Choose a valid application status.'
          else:
            cursor.execute(
                """
                UPDATE job_applications
                SET status = %s
                WHERE application_id = %s AND student_id = %s
                """,
                (status, application_id, session['student_id']),
            )
        elif action == 'contacted':
          application_id = int(request.form.get('application_id', '0'))
          cursor.execute(
              """
              UPDATE job_applications
              SET last_contacted = %s
              WHERE application_id = %s AND student_id = %s
              """,
              (date.today(), application_id, session['student_id']),
          )
        elif action == 'delete':
          application_id = int(request.form.get('application_id', '0'))
          cursor.execute(
              'DELETE FROM job_applications WHERE application_id=%s AND student_id=%s',
              (application_id, session['student_id']),
          )
        else:
          error = 'Unsupported tracker action.'
      if error:
        conn.rollback()
      else:
        conn.commit()
    except (ValueError, TypeError):
      if conn:
        conn.rollback()
      error = 'The application record could not be updated.'
    except Exception:
      if conn:
        conn.rollback()
      error = 'The application tracker is temporarily unavailable.'
    finally:
      if conn:
        conn.close()
    if not error:
      return redirect(url_for('career_tools.application_tracker', saved='1'))

  search = _clean(request.args.get('q'), 100)
  status_filter = _clean(request.args.get('status'), 30)
  priority_filter = _clean(request.args.get('priority'), 20)
  applications, metrics = _tracker_snapshot(search, status_filter, priority_filter)
  ai_insight = None
  if request.args.get('ai') == '1':
    with ai_feature_context('application_tracker', session.get('student_id')):
      ai_insight = pipeline_insights(_profile_context(), applications, metrics)
  return render_template(
      'tools/application_tracker.html',
      applications=applications, metrics=metrics, statuses=APPLICATION_STATUSES,
      priorities=APPLICATION_PRIORITIES, error=error, ai_insight=ai_insight,
      saved=request.args.get('saved') == '1', search=search,
      status_filter=status_filter, priority_filter=priority_filter,
      active_tool='application-tracker',
  )


@career_tools.route('/resume-tailor')
@login_required
def resume_tailor():
  return redirect(url_for('resume.resume_home', mode='tailor'))
