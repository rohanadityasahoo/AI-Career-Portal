import os

from flask import Blueprint, render_template, request, session
from werkzeug.utils import secure_filename
from database.db import get_db_connection
from ai_modules.resume_analyzer import extract_resume_text

from ai_modules.skill_analyzer import (
    detect_skills,
    calculate_skill_score,
    detect_career_domain,
    calculate_domain_skill_score,
    detect_sections,
    calculate_section_score,
    calculate_content_score,
    calculate_resume_ats_score,
    generate_recommendations
)

from ai_modules.ai_resume_analyzer import ( calculate_ai_resume_quality, recommend_ai_roles )

resume = Blueprint('resume', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):

    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@resume.route('/resume', methods=['GET', 'POST'])
def resume_home():

    if request.method == 'POST':

        # -----------------------------
        # Get uploaded file
        # -----------------------------

        if 'resume' not in request.files:
            return "No resume file selected"

        file = request.files['resume']

        if file.filename == '':
            return "No resume file selected"

        # -----------------------------
        # Validate PDF
        # -----------------------------

        if not allowed_file(file.filename):
            return "Only PDF files are allowed"


        # -----------------------------
        # Save Resume
        # -----------------------------

        filename = secure_filename(file.filename)

        os.makedirs(
            UPLOAD_FOLDER,
            exist_ok=True
        )

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        file.save(file_path)

        # -----------------------------
        # Extract Resume Text
        # -----------------------------

        resume_text = extract_resume_text(
            file_path
        )

        if not resume_text.strip():
            return "Could not extract text from this PDF"

        # -----------------------------
        # Detect Skills
        # -----------------------------

        detected_skills = detect_skills(
            resume_text
        )
        
        print("Detected Skills:", detected_skills)

        from ai_modules.job_recommender import recommend_jobs

        all_skills = []

        for category in detected_skills.values():
            all_skills.extend(category)

        all_skills = list(dict.fromkeys(all_skills))

        recommended_jobs = recommend_jobs(all_skills)
        
        print("All Skills:", all_skills)
        print("Recommended Jobs:", recommended_jobs)

        career_domain = detect_career_domain(
            detected_skills
        )

        skill_score = calculate_domain_skill_score(
            detected_skills,
            career_domain
        )

        print("Career Domain:", career_domain)
        print("Skill Score:", skill_score)

        # -----------------------------
        # Detect Resume Sections
        # -----------------------------

        detected_sections = detect_sections(
            resume_text
        )

        section_score = calculate_section_score(
            detected_sections
        )

        # -----------------------------
        # Content Score
        # -----------------------------

        content_score = calculate_content_score(
            resume_text
        )

        # -----------------------------
        # AI Resume Quality
        # -----------------------------

        ai_quality_score = calculate_ai_resume_quality(
            resume_text
        )
        
        ai_recommended_roles = recommend_ai_roles(
            resume_text
        )

        print(
            "AI Recommended Roles:",
            ai_recommended_roles
        )

        print("AI Resume Quality:", ai_quality_score)

        # -----------------------------
        # Final ATS Score
        # -----------------------------

        ats_score = calculate_resume_ats_score(
            ai_quality_score,
            skill_score,
            section_score,
            content_score
        )

        # -----------------------------
        # Final ATS Score
        # -----------------------------

        ats_score = calculate_resume_ats_score(
            ai_quality_score,
            skill_score,
            section_score,
            content_score
        )
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            
            insert into resume_analysis
            (
                student_id,
                resume_filename,
                ats_score,
                jd_match_percentage,
                skill_score,
                section_score,
                content_score,
                matched_skills,
                missing_skills
            )
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                session.get('student_id'),
                filename,
                ats_score,
                ats_score,
                skill_score,
                section_score,
                content_score,
                ", ".join(all_skills),
                ""
            )
        )

        conn.commit()

        cursor.close()
        conn.close()
        # -----------------------------
        # Recommendations
        # -----------------------------

        recommendations = generate_recommendations(
            [],
            detected_sections,
            content_score
        )

        # -----------------------------
        # Display Results
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

        )

    return render_template(
        'resume/upload.html'
    )
    
@resume.route('/resume/history')
def resume_history():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        select
            analysis_id,
            resume_filename,
            ats_score,
            jd_match_percentage,
            skill_score,
            section_score,
            content_score,
            created_at
        from resume_analysis
        order by created_at desc
        """
    )

    analyses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'resume/history.html',
        analyses=analyses
    )