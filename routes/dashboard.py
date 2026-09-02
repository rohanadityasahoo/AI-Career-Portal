from flask import Blueprint, render_template, session, redirect
from database.db import get_db_connection, ensure_career_roadmaps_table

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/dashboard')
def dashboard_home():

    if 'student_id' not in session:
        return redirect('/login')

    student_id = session['student_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # -----------------------------
    # Resume Statistics
    # -----------------------------

    cursor.execute(
        """
        select
            count(*) as resume_count,
            coalesce(max(ats_score), 0) as best_ats
        from resume_analysis
        where student_id = %s
        """,
        (student_id,)
    )

    resume_stats = cursor.fetchone()

    # -----------------------------
    # Interview Statistics
    # -----------------------------

    cursor.execute(
        """
        select
            count(*) as interview_count,
            coalesce(max(average_score), 0) as best_interview_score,
            coalesce(avg(average_score), 0) as average_interview_score,
            coalesce(
                (
                    select average_score
                    from interview_results
                    where student_id = %s
                    order by created_at desc, interview_id desc
                    limit 1
                ),
                0
            ) as latest_interview_score
        from interview_results
        where student_id = %s
        """,
        (student_id, student_id)
    )

    interview_stats = cursor.fetchone()

    # -----------------------------
    # Roadmap Statistics
    # -----------------------------

    ensure_career_roadmaps_table(cursor)

    cursor.execute(
        """
        select count(*) as roadmap_count
        from career_roadmaps
        where student_id = %s
        """,
        (student_id,)
    )

    roadmap_stats = cursor.fetchone()

    # -----------------------------
    # Close Database
    # -----------------------------

    cursor.close()
    conn.close()

    return render_template(
        'dashboard/index.html',
        student_name=session.get('student_name'),
        resume_count=resume_stats['resume_count'],
        best_ats=resume_stats['best_ats'],
        interview_count=interview_stats['interview_count'],
        best_interview_score=interview_stats['best_interview_score'],
        latest_interview_score=interview_stats['latest_interview_score'],
        average_interview_score=interview_stats['average_interview_score'],
        roadmap_count=roadmap_stats['roadmap_count']
    )
