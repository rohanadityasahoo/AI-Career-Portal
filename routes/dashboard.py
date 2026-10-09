from database.db import ensure_career_roadmaps_table, get_db_connection
from flask import Blueprint, render_template, session
from routes.auth import login_required

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/dashboard')
@login_required
def dashboard_home():
  student_id = session['student_id']

  conn = get_db_connection()
  try:
    with conn.cursor() as cursor:
      # -----------------------------
      # Resume Statistics
      # -----------------------------
      cursor.execute(
          """
                SELECT
                    count(*) AS resume_count,
                    coalesce(max(ats_score), 0) AS best_ats
                FROM resume_analysis
                WHERE student_id = %s
                """,
          (student_id,),
      )
      resume_stats = cursor.fetchone() or {'resume_count': 0, 'best_ats': 0}

      # -----------------------------
      # Interview Statistics
      # -----------------------------
      cursor.execute(
          """
                SELECT
                    count(*) AS interview_count,
                    coalesce(max(average_score), 0) AS best_interview_score,
                    coalesce(avg(average_score), 0) AS average_interview_score,
                    coalesce(
                        (
                            SELECT average_score
                            FROM interview_results
                            WHERE student_id = %s
                            ORDER BY created_at DESC, interview_id DESC
                            LIMIT 1
                        ),
                        0
                    ) AS latest_interview_score
                FROM interview_results
                WHERE student_id = %s
                """,
          (student_id, student_id),
      )
      interview_stats = cursor.fetchone() or {
          'interview_count': 0,
          'best_interview_score': 0,
          'average_interview_score': 0,
          'latest_interview_score': 0,
      }

      # -----------------------------
      # Roadmap Statistics
      # -----------------------------
      ensure_career_roadmaps_table(cursor)

      cursor.execute(
          """
                SELECT count(*) AS roadmap_count
                FROM career_roadmaps
                WHERE student_id = %s
                """,
          (student_id,),
      )
      roadmap_stats = cursor.fetchone() or {'roadmap_count': 0}

  finally:
    conn.close()

  return render_template(
      'dashboard/index.html',
      student_name=session.get('student_name', 'Student'),
      resume_count=resume_stats['resume_count'],
      best_ats=resume_stats['best_ats'],
      interview_count=interview_stats['interview_count'],
      best_interview_score=interview_stats['best_interview_score'],
      latest_interview_score=interview_stats['latest_interview_score'],
      average_interview_score=interview_stats['average_interview_score'],
      roadmap_count=roadmap_stats['roadmap_count'],
  )