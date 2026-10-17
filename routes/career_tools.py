import re
from datetime import date, datetime

from database.db import ensure_auth_schema, ensure_career_tools_schema, get_db_connection
from flask import Blueprint, Response, redirect, render_template, request, session, url_for
from routes.auth import login_required

career_tools = Blueprint('career_tools', __name__, url_prefix='/tools')

APPLICATION_STATUSES = (
    'Saved', 'Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn'
)
APPLICATION_PRIORITIES = ('High', 'Medium', 'Low')
WORK_PREFERENCES = ('Remote', 'Hybrid', 'On-site', 'Flexible')

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
  finally:
    conn.close()

  experienced = row.get('profile_type') == 'experienced'
  return {
      'full_name': row.get('full_name') or '',
      'profile_type': row.get('profile_type') or 'fresher',
      'current_job_title': row.get('current_job_title') or '',
      'current_company': row.get('current_company') or '',
      'skills': row.get('key_skills') or row.get('branch') or '',
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


def _tailoring_summary(form):
  required = _extract_skills(form.get('job_description'))
  available = _extract_skills(
      ' '.join((form.get('skills'), form.get('highlights'), form.get('current_job_title')))
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
  highlights = form['highlights'] or 'I have built practical experience solving problems, collaborating with stakeholders, and delivering reliable outcomes.'
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


@career_tools.route('/')
@login_required
def tools_home():
  return render_template(
      'tools/index.html',
      active_tool='home',
  )


@career_tools.route('/job-matcher', methods=['GET', 'POST'])
@login_required
def job_matcher():
  profile = _profile_context()
  form = {
      'target_role': _clean(request.form.get('target_role') or profile['target_role'], 120),
      'skills': _clean(request.form.get('skills') or profile['skills'], 1200),
      'location': _clean(request.form.get('location') or profile['preferred_location'], 150),
      'work_preference': _clean(request.form.get('work_preference') or profile['work_preference'], 30),
      'job_description': _clean(request.form.get('job_description'), 8000),
  }
  has_input = any(form.values())
  matches = _rank_roles(form['target_role'], form['skills'], form['job_description']) if has_input else []
  custom_fit = _custom_job_fit(form['target_role'], form['skills'], form['job_description'], form['location'], form['work_preference'])
  return render_template(
      'tools/job_matcher.html', profile=profile, form=form,
      matches=matches, custom_fit=custom_fit, active_tool='job-matcher',
  )


@career_tools.route('/skill-gap', methods=['GET', 'POST'])
@login_required
def skill_gap():
  profile = _profile_context()
  form = {
      'target_role': _clean(request.form.get('target_role') or profile['target_role'], 120),
      'skills': _clean(request.form.get('skills') or profile['skills'], 1200),
      'job_description': _clean(request.form.get('job_description'), 8000),
  }
  gap = _gap_report(form['target_role'], form['skills'], form['job_description'])
  return render_template(
      'tools/skill_gap.html', profile=profile, form=form,
      gap=gap, active_tool='skill-gap',
  )


@career_tools.route('/cover-letter', methods=['GET', 'POST'])
@login_required
def cover_letter():
  profile = _profile_context()
  form = {
      'company': _clean(request.form.get('company'), 150),
      'target_role': _clean(request.form.get('target_role') or profile['target_role'], 150),
      'skills': _clean(request.form.get('skills') or profile['skills'], 1200),
      'highlights': _clean(request.form.get('highlights') or profile['career_highlights'], 1200),
      'job_description': _clean(request.form.get('job_description'), 4000),
      'full_name': profile['full_name'],
      'current_job_title': profile['current_job_title'],
      'current_company': profile['current_company'],
  }
  error = None
  letter = None
  tailoring = _tailoring_summary(form)
  if request.method == 'POST':
    if not form['company'] or not form['target_role']:
      error = 'Add both the company name and target role to create a draft.'
    else:
      letter = _cover_letter(form)
      if request.form.get('action') == 'download':
        filename = re.sub(r'[^a-z0-9]+', '-', form['target_role'].lower()).strip('-') or 'cover-letter'
        return Response(
            letter,
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment; filename={filename}-cover-letter.txt'},
        )
  return render_template(
      'tools/cover_letter.html', profile=profile, form=form,
      letter=letter, tailoring=tailoring, error=error, active_tool='cover-letter',
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
  return render_template(
      'tools/application_tracker.html',
      applications=applications, metrics=metrics, statuses=APPLICATION_STATUSES,
      priorities=APPLICATION_PRIORITIES, error=error,
      saved=request.args.get('saved') == '1', search=search,
      status_filter=status_filter, priority_filter=priority_filter,
      active_tool='application-tracker',
  )


@career_tools.route('/resume-tailor')
@login_required
def resume_tailor():
  return redirect(url_for('resume.resume_home', mode='tailor'))