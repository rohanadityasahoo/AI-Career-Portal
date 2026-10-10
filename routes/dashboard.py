from datetime import datetime

from ai_modules.career_ai import build_dashboard_guidance, generate_dashboard_guidance
from database.db import ensure_career_roadmaps_table, get_db_connection
from flask import Blueprint, jsonify, render_template, session, url_for
from routes.auth import login_required


dashboard = Blueprint('dashboard', __name__)


def _score(value):
  """Return display-safe numeric scores while preserving absent values."""
  if value is None:
    return None
  try:
    return round(float(value), 1)
  except (TypeError, ValueError):
    return None


def _skills(value):
  """Turn the legacy comma-separated skill field into a bounded list."""
  if not value:
    return []
  skills = []
  for item in str(value).split(','):
    item = item.strip()
    if item and item not in skills:
      skills.append(item)
    if len(skills) == 8:
      break
  return skills


def _format_date(value):
  if not value:
    return 'Not yet'
  if isinstance(value, datetime):
    return value.strftime('%d %b %Y')
  return str(value)


def _action_links():
  """Keep AI output limited to action keys, never arbitrary URLs."""
  return {
      'profile': {
          'url': url_for('profile.student_profile'),
          'label': 'Update profile',
      },
      'resume': {
          'url': url_for('resume.resume_home'),
          'label': 'Review resume',
      },
      'interview': {
          'url': url_for('interview.interview_home'),
          'label': 'Practice interview',
      },
      'roadmap': {
          'url': url_for('roadmap.roadmap_page'),
          'label': 'Open roadmap',
      },
      'chat': {
          'url': url_for('chatbot.chatbot_home'),
          'label': 'Ask CareerPilot',
      },
  }


def _add_action_links(guidance):
  links = _action_links()
  enriched = dict(guidance)

  def enrich(action):
    action = dict(action or {})
    action_config = links.get(action.get('action_key'), links['profile'])
    action['url'] = action_config['url']
    action['label'] = action_config['label']
    return action

  enriched['next_action'] = enrich(guidance.get('next_action'))
  enriched['weekly_plan'] = [
      enrich(action) for action in guidance.get('weekly_plan', [])
  ]
  return enriched


def _dashboard_snapshot(student_id):
  """Load the small, factual record used by dashboard UI and AI coaching."""
  conn = get_db_connection()
  try:
    with conn.cursor() as cursor:
      ensure_career_roadmaps_table(cursor)

      cursor.execute(
          """
          SELECT s.branch, s.year, p.semester, p.cgpa, p.career_goal,
                 p.target_role, p.preferred_industry
          FROM students AS s
          LEFT JOIN student_profile AS p ON p.student_id = s.student_id
          WHERE s.student_id = %s
          """,
          (student_id,),
      )
      profile = cursor.fetchone() or {}

      cursor.execute(
          """
          SELECT COUNT(*) AS resume_count, MAX(created_at) AS last_resume_at
          FROM resume_analysis
          WHERE student_id = %s
          """,
          (student_id,),
      )
      resume_stats = cursor.fetchone() or {}
      cursor.execute(
          """
          SELECT ats_score, matched_skills, missing_skills, created_at
          FROM resume_analysis
          WHERE student_id = %s
          ORDER BY created_at DESC, analysis_id DESC
          LIMIT 1
          """,
          (student_id,),
      )
      latest_resume = cursor.fetchone() or {}

      cursor.execute(
          """
          SELECT COUNT(*) AS interview_count,
                 COALESCE(MAX(average_score), 0) AS best_interview_score,
                 COALESCE(AVG(average_score), 0) AS average_interview_score
          FROM interview_results
          WHERE student_id = %s
          """,
          (student_id,),
      )
      interview_stats = cursor.fetchone() or {}
      cursor.execute(
          """
          SELECT role, average_score, created_at
          FROM interview_results
          WHERE student_id = %s
          ORDER BY created_at DESC, interview_id DESC
          LIMIT 2
          """,
          (student_id,),
      )
      latest_interviews = cursor.fetchall() or []

      cursor.execute(
          """
          SELECT target_role, updated_at
          FROM career_roadmaps
          WHERE student_id = %s
          LIMIT 1
          """,
          (student_id,),
      )
      roadmap = cursor.fetchone() or {}
  finally:
    conn.close()

  resume_count = int(resume_stats.get('resume_count') or 0)
  interview_count = int(interview_stats.get('interview_count') or 0)
  roadmap_count = 1 if roadmap else 0
  target_role = (profile.get('target_role') or roadmap.get('target_role') or '').strip()
  latest_interview = latest_interviews[0] if latest_interviews else {}
  latest_score = _score(latest_interview.get('average_score'))
  previous_score = (
      _score(latest_interviews[1].get('average_score'))
      if len(latest_interviews) > 1
      else None
  )
  profile_fields = [
      target_role,
      profile.get('career_goal'),
      profile.get('branch'),
      profile.get('year'),
  ]
  profile_complete = sum(bool(item) for item in profile_fields) >= 3
  milestones = [
      {'label': 'Profile completed', 'complete': profile_complete, 'action_key': 'profile'},
      {'label': 'Resume reviewed', 'complete': bool(resume_count), 'action_key': 'resume'},
      {'label': 'Interview practised', 'complete': bool(interview_count), 'action_key': 'interview'},
      {'label': 'Roadmap saved', 'complete': bool(roadmap_count), 'action_key': 'roadmap'},
  ]
  completion_score = round(
      100 * sum(item['complete'] for item in milestones) / len(milestones)
  )

  activities = []
  if latest_resume.get('created_at'):
    activities.append({
        'title': 'Resume review completed',
        'detail': 'Latest readiness signal: ' + (
            f"{_score(latest_resume.get('ats_score'))}/100"
            if _score(latest_resume.get('ats_score')) is not None
            else 'available in your resume review'
        ),
        'date': _format_date(latest_resume.get('created_at')),
        'action_key': 'resume',
        '_sort': latest_resume.get('created_at'),
    })
  if latest_interview.get('created_at'):
    activities.append({
        'title': 'Interview practice completed',
        'detail': (
            f"{latest_interview.get('role', 'Practice interview')} · "
            f"{latest_score}/100"
        ),
        'date': _format_date(latest_interview.get('created_at')),
        'action_key': 'interview',
        '_sort': latest_interview.get('created_at'),
    })
  if roadmap.get('updated_at'):
    activities.append({
        'title': 'Career roadmap saved',
        'detail': roadmap.get('target_role') or 'Career preparation roadmap',
        'date': _format_date(roadmap.get('updated_at')),
        'action_key': 'roadmap',
        '_sort': roadmap.get('updated_at'),
    })
  activities.sort(key=lambda item: item['_sort'], reverse=True)
  for activity in activities:
    activity.pop('_sort', None)

  return {
      'profile': {
          'target_role': target_role,
          'career_goal': profile.get('career_goal') or '',
          'branch': profile.get('branch') or '',
          'year': profile.get('year') or '',
          'cgpa': _score(profile.get('cgpa')),
          'complete': profile_complete,
      },
      'resume': {
          'count': resume_count,
          'latest_score': _score(latest_resume.get('ats_score')),
          'matched_skills': _skills(latest_resume.get('matched_skills')),
          'missing_skills': _skills(latest_resume.get('missing_skills')),
          'last_updated': _format_date(resume_stats.get('last_resume_at')),
      },
      'interview': {
          'count': interview_count,
          'best_score': _score(interview_stats.get('best_interview_score')) if interview_count else None,
          'average_score': _score(interview_stats.get('average_interview_score')) if interview_count else None,
          'latest_score': latest_score,
          'change': round(latest_score - previous_score, 1) if latest_score is not None and previous_score is not None else None,
          'last_role': latest_interview.get('role') or '',
      },
      'roadmap': {
          'count': roadmap_count,
          'target_role': roadmap.get('target_role') or '',
          'last_updated': _format_date(roadmap.get('updated_at')),
      },
      'milestones': milestones,
      'completion_score': completion_score,
      'activities': activities[:3],
  }


@dashboard.route('/dashboard')
@login_required
def dashboard_home():
  progress = _dashboard_snapshot(session['student_id'])
  guidance = _add_action_links(build_dashboard_guidance(progress))

  return render_template(
      'dashboard/index.html',
      student_name=session.get('student_name', 'Student'),
      progress=progress,
      guidance=guidance,
      action_links=_action_links(),
      dashboard_ai_url=url_for('dashboard.dashboard_ai_insight'),
  )


@dashboard.post('/dashboard/ai-insight')
@login_required
def dashboard_ai_insight():
  """Generate fresh optional AI coaching without blocking dashboard loading."""
  progress = _dashboard_snapshot(session['student_id'])
  guidance = _add_action_links(generate_dashboard_guidance(progress))
  return jsonify({'guidance': guidance})
