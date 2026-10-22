import json
from collections.abc import Mapping

from ai_modules.career_ai import (
    generate_roadmap as generate_roadmap_with_groq,
    normalise_roadmap,
)
from ai_modules.usage import ai_feature_context
from database.db import ensure_career_roadmaps_table, get_db_connection
from flask import Blueprint, jsonify, render_template, request, session, url_for
from routes.auth import login_required

roadmap = Blueprint('roadmap', __name__)

MAX_TARGET_ROLE_LENGTH = 120


def _student_context(student_id):
  """Return only the profile facts that can personalise a roadmap."""
  conn = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      cursor.execute(
          """
          SELECT s.profile_type, s.branch, s.year,
                  fresher_profile.semester, fresher_profile.cgpa,
                  COALESCE(fresher_profile.career_goal, professional_profile.career_switch_reason) AS career_goal,
                  COALESCE(fresher_profile.target_role, professional_profile.target_role) AS target_role,
                  COALESCE(fresher_profile.preferred_industry, professional_profile.current_industry, professional_profile.target_field) AS preferred_industry,
                  COALESCE(fresher_profile.preferred_location, professional_profile.preferred_location) AS preferred_location,
                  professional_profile.current_job_title,
                  professional_profile.current_company,
                  professional_profile.key_skills,
                  professional_profile.job_search_status,
                  professional_profile.target_companies,
                  professional_profile.employment_type,
                  professional_profile.work_preference,
                  professional_profile.relocation_preference,
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
          (student_id,),
      )
      return cursor.fetchone()
  except Exception:
    # A roadmap can still be useful without optional profile context.
    return None
  finally:
    if conn:
      conn.close()


def _action_links():
  """Keep roadmap action links server-controlled rather than AI-controlled."""
  return {
      'profile': url_for('profile.student_profile'),
      'resume': url_for('resume.resume_home'),
      'interview': url_for('interview.interview_home'),
      'chatbot': url_for('chatbot.chatbot_home'),
  }


def _render_roadmap(**context):
  defaults = {
      'target_role': '',
      'roadmap': None,
      'error': '',
      'storage_warning': '',
      'action_links': _action_links(),
  }
  defaults.update(context)
  return render_template('roadmap/index.html', **defaults)


@roadmap.route('/roadmap', methods=['GET', 'POST'])
@login_required
def roadmap_page():
  student_id = session['student_id']

  if request.method == 'GET':
    conn = None
    target_role = ''
    roadmap_data = None
    storage_warning = ''
    try:
      conn = get_db_connection()
      with conn.cursor() as cursor:
        ensure_career_roadmaps_table(cursor)
        cursor.execute(
            """
            SELECT target_role, roadmap_json
            FROM career_roadmaps
            WHERE student_id = %s
            """,
            (student_id,),
        )
        saved = cursor.fetchone()

        if saved:
          target_role = str(saved.get('target_role') or '').strip()
          if saved.get('roadmap_json'):
            try:
              stored_roadmap = saved['roadmap_json']
              raw_roadmap = (
                  json.loads(stored_roadmap)
                  if isinstance(stored_roadmap, (str, bytes, bytearray))
                  else stored_roadmap
              )
              roadmap_data = normalise_roadmap(raw_roadmap, target_role)
              if len(roadmap_data['steps']) != 7:
                roadmap_data = None
                storage_warning = 'Your saved roadmap is incomplete. Generate a fresh roadmap to replace it.'
            except (TypeError, ValueError):
              storage_warning = 'Your saved roadmap could not be read. Generate a fresh roadmap to replace it.'

        if not target_role:
          cursor.execute(
              """
              SELECT COALESCE(fresher_profile.target_role, professional_profile.target_role) AS target_role
              FROM students AS s
              LEFT JOIN student_profile AS fresher_profile
                  ON fresher_profile.student_id = s.student_id
                 AND s.profile_type = 'fresher'
              LEFT JOIN professional_profile
                  ON professional_profile.student_id = s.student_id
                 AND s.profile_type = 'experienced'
              WHERE s.student_id = %s
              """,
              (student_id,),
          )
          profile_data = cursor.fetchone() or {}
          target_role = str(profile_data.get('target_role') or '').strip()
    except Exception:
      storage_warning = 'Your saved roadmap is temporarily unavailable. You can still create a new plan.'
    finally:
      if conn:
        conn.close()

    return _render_roadmap(
        target_role=target_role,
        roadmap=roadmap_data,
        storage_warning=storage_warning,
    )

  data = request.get_json(silent=True) if request.is_json else request.form
  if not isinstance(data, Mapping):
    data = {}
  target_role = str(data.get('target_role') or data.get('career') or '').strip()

  if not target_role:
    error = 'Enter a target role to generate a roadmap.'
    if request.is_json:
      return jsonify({'error': error}), 400
    return _render_roadmap(error=error)

  if len(target_role) > MAX_TARGET_ROLE_LENGTH:
    error = f'Please keep the target role within {MAX_TARGET_ROLE_LENGTH} characters.'
    if request.is_json:
      return jsonify({'error': error}), 400
    return _render_roadmap(target_role=target_role, error=error)

  with ai_feature_context('roadmap_generator', student_id):
    roadmap_data = generate_roadmap_with_groq(
        target_role, _student_context(student_id)
    )

  saved = True
  storage_warning = ''
  conn = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      ensure_career_roadmaps_table(cursor)
      cursor.execute(
          """
          INSERT INTO career_roadmaps (student_id, target_role, roadmap_json)
          VALUES (%s, %s, %s)
          ON DUPLICATE KEY UPDATE
              target_role = VALUES(target_role),
              roadmap_json = VALUES(roadmap_json)
          """,
          (student_id, target_role, json.dumps(roadmap_data)),
      )
    conn.commit()
  except Exception:
    saved = False
    storage_warning = 'Your roadmap is ready, but it could not be saved right now.'
  finally:
    if conn:
      conn.close()

  if request.is_json:
    return jsonify({
        'target_role': target_role,
        'roadmap': roadmap_data,
        'saved': saved,
        'warning': storage_warning or None,
    })

  return _render_roadmap(
      target_role=target_role,
      roadmap=roadmap_data,
      storage_warning=storage_warning,
  )
