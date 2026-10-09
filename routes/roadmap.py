import json
from ai_modules.roadmap_generator import generate_roadmap
from database.db import ensure_career_roadmaps_table, get_db_connection
from flask import Blueprint, jsonify, redirect, render_template, request, session
from routes.auth import login_required

roadmap = Blueprint('roadmap', __name__)


@roadmap.route('/roadmap', methods=['GET', 'POST'])
@login_required
def roadmap_page():
  student_id = session['student_id']

  # ==========================================
  # GET REQUEST: Display current / saved roadmap
  # ==========================================
  if request.method == 'GET':
    conn = get_db_connection()
    target_role = ''
    roadmap_steps = None

    try:
      with conn.cursor() as cursor:
        ensure_career_roadmaps_table(cursor)

        # Check if student already has a saved roadmap
        cursor.execute(
            """
                    SELECT target_role, roadmap_json
                    FROM career_roadmaps
                    WHERE student_id = %s
                    """,
            (student_id,),
        )
        saved = cursor.fetchone()

        if saved and saved.get('roadmap_json'):
          try:
            roadmap_steps = json.loads(saved['roadmap_json'])
            target_role = saved.get('target_role', '')
          except Exception:
            roadmap_steps = None

        # Fallback to student profile target_role if none saved
        if not target_role:
          cursor.execute(
              """
                        SELECT target_role
                        FROM student_profile
                        WHERE student_id = %s
                        """,
              (student_id,),
          )
          profile_data = cursor.fetchone()
          if profile_data:
            target_role = profile_data.get('target_role') or ''
    finally:
      conn.close()

    return render_template(
        'roadmap/index.html',
        roadmap_steps=roadmap_steps,
        target_role=target_role,
    )

  # ==========================================
  # POST REQUEST: Generate & persist roadmap
  # ==========================================
  data = request.get_json(silent=True) if request.is_json else request.form
  target_role = (data.get('target_role') or data.get('career') or '').strip()

  if not target_role:
    err_msg = 'Please enter a target role.'
    if request.is_json:
      return jsonify({'error': err_msg}), 400
    return (
        render_template(
            'roadmap/index.html', roadmap_steps=None, error=err_msg
        ),
        400,
    )

  # Generate steps using expanded roadmap knowledge base
  roadmap_data = generate_roadmap(target_role)

  # Save to database
  conn = get_db_connection()
  try:
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
  finally:
    conn.close()

  if request.is_json:
    return jsonify({'target_role': target_role, 'roadmap': roadmap_data})

  return render_template(
      'roadmap/index.html', target_role=target_role, roadmap_steps=roadmap_data
  )