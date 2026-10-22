import os
import uuid

from ai_modules.career_ai import analyze_resume
from ai_modules.resume_analyzer import extract_resume_text
from ai_modules.usage import ai_feature_context
from database.db import (
    ensure_auth_schema,
    ensure_resume_analysis_schema,
    get_db_connection,
)
from flask import Blueprint, current_app, redirect, render_template, request, session
from werkzeug.utils import secure_filename

resume = Blueprint('resume', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
  return (
      '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
  )


def clean_optional_text(value, limit):
  """Keep optional tailoring inputs bounded before processing or sending them."""
  return ' '.join(str(value or '').split())[:limit]


def _student_profile_type():
  """Return the signed-in student's resume coaching track."""
  conn = get_db_connection()
  try:
    with conn.cursor() as cursor:
      ensure_auth_schema(cursor)
      conn.commit()
      cursor.execute(
          'SELECT profile_type FROM students WHERE student_id = %s',
          (session['student_id'],),
      )
      row = cursor.fetchone() or {}
  finally:
    conn.close()
  return 'experienced' if row.get('profile_type') == 'experienced' else 'fresher'


def _upload_page(profile_type, tool_mode, error=None):
  return render_template(
      'resume/upload.html',
      profile_type=profile_type,
      tool_mode=tool_mode,
      error=error,
  )


@resume.route('/resume', methods=['GET', 'POST'])
def resume_home():
  if 'student_id' not in session:
    return redirect('/login')

  profile_type = _student_profile_type()
  tool_mode = (
      request.args.get('mode') == 'tailor'
      or request.form.get('mode') == 'tailor'
  )

  if request.method == 'POST':
    if 'resume' not in request.files:
      return _upload_page(profile_type, tool_mode, 'No resume file selected.'), 400

    file = request.files['resume']
    if not file or file.filename == '':
      return _upload_page(profile_type, tool_mode, 'No resume file selected.'), 400

    if not allowed_file(file.filename):
      return _upload_page(profile_type, tool_mode, 'Only PDF files are allowed.'), 400

    # Check the PDF signature before handing the upload to a parser.
    file_header = file.stream.read(8)
    file.stream.seek(0)
    if not file_header.startswith(b'%PDF-'):
      return _upload_page(
          profile_type,
          tool_mode,
          'The uploaded file does not appear to be a valid PDF.',
      ), 400

    target_role = clean_optional_text(request.form.get('target_role'), 120)
    job_description = clean_optional_text(
        request.form.get('job_description'), 8000
    )

    safe_name = secure_filename(file.filename) or 'resume.pdf'
    unique_filename = (
        f"student_{session['student_id']}_{uuid.uuid4().hex[:8]}_{safe_name}"
    )
    upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, unique_filename)

    try:
      file.save(file_path)
      resume_text = extract_resume_text(file_path)
    except OSError:
      return _upload_page(
          profile_type,
          tool_mode,
          'We could not process this upload. Please try the PDF again.',
      ), 500
    finally:
      # Analysis uses extracted text only; source resumes are not retained.
      try:
        os.remove(file_path)
      except OSError:
        pass

    if not resume_text or not resume_text.strip():
      return _upload_page(
          profile_type,
          tool_mode,
          'Could not extract readable text from this PDF.',
      ), 400

    with ai_feature_context('resume_analyzer', session.get('student_id')):
      ai_feedback = analyze_resume(
          resume_text,
          target_role=target_role,
          job_description=job_description,
          profile_type=profile_type,
      )
    if not ai_feedback:
      return _upload_page(
          profile_type,
          tool_mode,
          'We could not analyze the readable text in this PDF. Please try another file.',
      ), 503

    missing_skills = ai_feedback.get('skill_gaps', [])
    detected_skills = ai_feedback.get('detected_skills', [])
    scores = ai_feedback.get('scores', {})
    job_alignment = ai_feedback.get('job_alignment') or {}

    history_saved = True
    conn = None
    try:
      conn = get_db_connection()
      with conn.cursor() as cursor:
        ensure_resume_analysis_schema(cursor)
        cursor.execute(
            """
            INSERT INTO resume_analysis (
                student_id,
                profile_type,
                resume_filename,
                ats_score,
                jd_match_percentage,
                skill_score,
                section_score,
                content_score,
                matched_skills,
                missing_skills
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session.get('student_id'),
                profile_type,
                safe_name,
                ai_feedback.get('overall_score'),
                job_alignment.get('score'),
                scores.get('Skill visibility'),
                scores.get('Section coverage'),
                scores.get('Content evidence'),
                ', '.join(detected_skills),
                ', '.join(missing_skills),
            ),
        )
      conn.commit()
    except Exception:
      current_app.logger.exception('Could not save resume analysis history.')
      history_saved = False
    finally:
      if conn:
        conn.close()

    return render_template(
        'resume/result.html',
        ai_feedback=ai_feedback,
        history_saved=history_saved,
        profile_type=profile_type,
    )

  return _upload_page(profile_type, tool_mode)


@resume.route('/resume/history')
def resume_history():
  if 'student_id' not in session:
    return redirect('/login')

  conn = get_db_connection()
  try:
    with conn.cursor() as cursor:
      ensure_resume_analysis_schema(cursor)
      conn.commit()
      cursor.execute(
          """
          SELECT analysis_id, profile_type, resume_filename, created_at
          FROM resume_analysis
          WHERE student_id = %s
          ORDER BY created_at DESC, analysis_id DESC
          """,
          (session['student_id'],),
      )
      analyses = cursor.fetchall()
  finally:
    conn.close()

  return render_template('resume/history.html', analyses=analyses)
