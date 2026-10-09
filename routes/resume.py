import os
import uuid
from ai_modules.ai_resume_analyzer import (
    calculate_ai_resume_quality,
    recommend_ai_roles,
)
from ai_modules.job_recommender import recommend_jobs
from ai_modules.resume_analyzer import extract_resume_text
from ai_modules.skill_analyzer import (
    calculate_content_score,
    calculate_domain_skill_score,
    calculate_resume_ats_score,
    calculate_section_score,
    detect_career_domain,
    detect_sections,
    detect_skills,
    generate_recommendations,
)
from database.db import get_db_connection
from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

resume = Blueprint('resume', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
  return (
      '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
  )


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

    # -----------------------------
    # Save Resume with unique name
    # -----------------------------
    safe_name = secure_filename(file.filename)
    unique_filename = (
        f"student_{session['student_id']}_{uuid.uuid4().hex[:8]}_{safe_name}"
    )

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)

    # -----------------------------
    # Extract Resume Text
    # -----------------------------
    resume_text = extract_resume_text(file_path)

    if not resume_text or not resume_text.strip():
      return (
          render_template(
              'resume/upload.html',
              error='Could not extract readable text from this PDF.',
          ),
          400,
      )

    # -----------------------------
    # Detect Skills & Recommend Jobs
    # -----------------------------
    detected_skills = detect_skills(resume_text)

    all_skills = []
    for category in detected_skills.values():
      all_skills.extend(category)
    all_skills = list(dict.fromkeys(all_skills))

    recommended_jobs = recommend_jobs(all_skills)

    career_domain = detect_career_domain(detected_skills)
    skill_score = calculate_domain_skill_score(detected_skills, career_domain)

    # -----------------------------
    # Sections & Content Scores
    # -----------------------------
    detected_sections = detect_sections(resume_text)
    section_score = calculate_section_score(detected_sections)
    content_score = calculate_content_score(resume_text)

    # -----------------------------
    # AI Quality & Role Matches
    # -----------------------------
    ai_quality_score = calculate_ai_resume_quality(resume_text)
    ai_recommended_roles = recommend_ai_roles(resume_text)

    # -----------------------------
    # Final ATS Score (single calculation)
    # -----------------------------
    ats_score = calculate_resume_ats_score(
        ai_quality_score, skill_score, section_score, content_score
    )

    # -----------------------------
    # Database Persistence
    # -----------------------------
    conn = get_db_connection()
    try:
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
                safe_name,  # display original clean filename to user
                ats_score,
                ats_score,
                skill_score,
                section_score,
                content_score,
                ', '.join(all_skills),
                '',
            ),
        )
      conn.commit()
    finally:
      conn.close()

    # -----------------------------
    # Recommendations
    # -----------------------------
    recommendations = generate_recommendations(
        [], detected_sections, content_score
    )

    # -----------------------------
    # Render Results
    # -----------------------------
    return render_template(
        'resume/result.html',
        ats_score=ats_score,
        ai_quality_score=ai_quality_score,
        career_domain=career_domain,
        ai_recommended_roles=ai_recommended_roles,
        student_id=session.get('student_id'),
        recommended_jobs=recommended_jobs,
        detected_skills=detected_skills,
        matched_skills=all_skills,
        missing_skills=[],
        detected_sections=detected_sections,
        section_score=section_score,
        skill_score=skill_score,
        content_score=content_score,
        recommendations=recommendations,
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
                    ats_score,
                    jd_match_percentage,
                    skill_score,
                    section_score,
                    content_score,
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