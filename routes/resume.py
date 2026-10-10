import os
import uuid
from ai_modules.career_ai import analyze_resume
from ai_modules.resume_analyzer import extract_resume_text
from database.db import get_db_connection
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


@resume.route('/resume', methods=['GET', 'POST'])
def resume_home():
  if 'student_id' not in session:
    return redirect('/login')

  if request.method == 'POST':
    # -----------------------------
    # Validate uploaded file
    # -----------------------------
    if 'resume' not in request.files:
      return (
          render_template(
              'resume/upload.html', error='No resume file selected.'
          ),
          400,
      )

    file = request.files['resume']

    if not file or file.filename == '':
      return (
          render_template(
              'resume/upload.html', error='No resume file selected.'
          ),
          400,
      )

    if not allowed_file(file.filename):
      return (
          render_template(
              'resume/upload.html', error='Only PDF files are allowed.'
          ),
          400,
      )

    # File extensions are only a convenience signal. Check the PDF signature
    # as well before handing the upload to a PDF parser.
    file_header = file.stream.read(8)
    file.stream.seek(0)
    if not file_header.startswith(b'%PDF-'):
      return (
          render_template(
              'resume/upload.html',
              error='The uploaded file does not appear to be a valid PDF.',
          ),
          400,
      )

    target_role = clean_optional_text(request.form.get('target_role'), 120)
    job_description = clean_optional_text(
        request.form.get('job_description'), 8000
    )

    # -----------------------------
    # Save Resume with unique name
    # -----------------------------
    safe_name = secure_filename(file.filename) or 'resume.pdf'
    unique_filename = (
        f"student_{session['student_id']}_{uuid.uuid4().hex[:8]}_{safe_name}"
    )

    upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, unique_filename)

    # -----------------------------
    # Extract Resume Text
    # -----------------------------
    try:
      file.save(file_path)
      resume_text = extract_resume_text(file_path)
    except OSError:
      return (
          render_template(
              'resume/upload.html',
              error='We could not process this upload. Please try the PDF again.',
          ),
          500,
      )
    finally:
      # Analysis uses extracted text only; retaining a student's source resume
      # would create an unnecessary privacy and storage burden.
      try:
        os.remove(file_path)
      except OSError:
        pass

    if not resume_text or not resume_text.strip():
      return (
          render_template(
              'resume/upload.html',
              error='Could not extract readable text from this PDF.',
          ),
          400,
      )

    # Local evidence is always calculated; Groq adds a detailed editorial
    # layer when configured. The analysis therefore remains useful if the
    # AI provider is unavailable.
    ai_feedback = analyze_resume(
        resume_text,
        target_role=target_role,
        job_description=job_description,
    )
    if not ai_feedback:
      return (
          render_template(
              'resume/upload.html',
              error='We could not analyze the readable text in this PDF. Please try another file.',
          ),
          503,
      )

    missing_skills = ai_feedback.get('skill_gaps', [])
    detected_skills = ai_feedback.get('detected_skills', [])
    scores = ai_feedback.get('scores', {})
    job_alignment = ai_feedback.get('job_alignment') or {}

    # -----------------------------
    # Database Persistence
    # -----------------------------
    history_saved = True
    conn = None
    try:
      conn = get_db_connection()
      with conn.cursor() as cursor:
        cursor.execute(
            """
                    INSERT INTO resume_analysis (
                        student_id,
                        resume_filename,
                        ats_score,
                        jd_match_percentage,
                        skill_score,
                        section_score,
                        content_score,
                        matched_skills,
                        missing_skills
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
            (
                session.get('student_id'),
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
      # The current analysis should not be discarded if history storage is
      # temporarily down. No resume text is written to the application log.
      current_app.logger.exception('Could not save resume analysis history.')
      history_saved = False
    finally:
      if conn:
        conn.close()

    return render_template(
        'resume/result.html', ai_feedback=ai_feedback, history_saved=history_saved
    )

  return render_template('resume/upload.html')


@resume.route('/resume/history')
def resume_history():
  if 'student_id' not in session:
    return redirect('/login')

  conn = get_db_connection()
  try:
    with conn.cursor() as cursor:
      cursor.execute(
          """
                SELECT
                    analysis_id,
                    resume_filename,
                    created_at
                FROM resume_analysis
                WHERE student_id = %s
                ORDER BY created_at DESC
                """,
          (session['student_id'],),
      )
      analyses = cursor.fetchall()
  finally:
    conn.close()

  return render_template('resume/history.html', analyses=analyses)
