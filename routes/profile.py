import os
from database.db import get_db_connection
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from routes.auth import login_required
from werkzeug.utils import secure_filename

profile = Blueprint('profile', __name__)

# ==========================================
# PROFILE PHOTO SETTINGS
# ==========================================

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'uploads', 'profiles'
)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
  return (
      '.' in filename
      and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
  )


# ==========================================
# PROFILE PAGE
# ==========================================


@profile.route('/profile', methods=['GET', 'POST'])
@login_required
def student_profile():
  student_id = session['student_id']
  conn = get_db_connection()

  try:
    with conn.cursor() as cursor:
      # ==========================================
      # SAVE PROFILE (POST)
      # ==========================================
      if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        gender = request.form.get('gender')
        college = request.form.get('college', '').strip()
        branch = request.form.get('branch', '').strip()
        year = request.form.get('year')

        semester = request.form.get('semester')
        cgpa_raw = request.form.get('cgpa', '').strip()
        career_goal = request.form.get('career_goal', '').strip()
        target_role = request.form.get('target_role', '').strip()
        preferred_industry = request.form.get('preferred_industry', '').strip()
        preferred_location = request.form.get('preferred_location', '').strip()

        # Parse CGPA safely
        cgpa = None
        if cgpa_raw:
          try:
            cgpa = float(cgpa_raw)
          except ValueError:
            cgpa = None

        # -----------------------------
        # Update Students Table
        # -----------------------------
        cursor.execute(
            """
                    UPDATE students
                    SET full_name=%s, phone=%s, gender=%s, college=%s, branch=%s, year=%s
                    WHERE student_id=%s
                    """,
            (full_name, phone, gender, college, branch, year, student_id),
        )

        # -----------------------------
        # Save Profile Photo
        # -----------------------------
        profile_photo = request.files.get('profile_photo')
        if profile_photo and profile_photo.filename:
          if allowed_file(profile_photo.filename):
            extension = profile_photo.filename.rsplit('.', 1)[1].lower()
            photo_filename = secure_filename(
                f'student_{student_id}.{extension}'
            )

            # Clean previous extensions
            for old_ext in ALLOWED_EXTENSIONS:
              old_path = os.path.join(
                  UPLOAD_FOLDER, f'student_{student_id}.{old_ext}'
              )
              if os.path.exists(old_path):
                os.remove(old_path)

            profile_photo.save(os.path.join(UPLOAD_FOLDER, photo_filename))

            cursor.execute(
                """
                            UPDATE students
                            SET profile_photo=%s
                            WHERE student_id=%s
                            """,
                (photo_filename, student_id),
            )
          else:
            flash(
                'Invalid photo format. Only JPG, JPEG, and PNG are allowed.',
                'warning',
            )

        # -----------------------------
        # Update or Insert Career Profile
        # -----------------------------
        cursor.execute(
            """
                    INSERT INTO student_profile (
                        student_id, semester, cgpa, career_goal, target_role,
                        preferred_industry, preferred_location
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        semester=VALUES(semester),
                        cgpa=VALUES(cgpa),
                        career_goal=VALUES(career_goal),
                        target_role=VALUES(target_role),
                        preferred_industry=VALUES(preferred_industry),
                        preferred_location=VALUES(preferred_location)
                    """,
            (
                student_id,
                semester,
                cgpa,
                career_goal,
                target_role,
                preferred_industry,
                preferred_location,
            ),
        )

        conn.commit()

        if full_name:
          session['student_name'] = full_name

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.student_profile'))

      # ==========================================
      # LOAD PROFILE (GET)
      # ==========================================
      cursor.execute(
          """
                SELECT student_id, full_name, email, phone, gender, college, branch, year, profile_photo
                FROM students
                WHERE student_id=%s
                """,
          (student_id,),
      )
      student = cursor.fetchone()

      cursor.execute(
          """
                SELECT semester, cgpa, career_goal, target_role, preferred_industry, preferred_location
                FROM student_profile
                WHERE student_id=%s
                """,
          (student_id,),
      )
      career_profile = cursor.fetchone()

  finally:
    conn.close()

  return render_template(
      'profile/index.html', student=student, career_profile=career_profile
  )


# ==========================================
# SERVE PROFILE PHOTO
# ==========================================


@profile.route('/profile/photo/<filename>')
@login_required
def profile_photo(filename):
  safe_name = secure_filename(filename)
  return send_from_directory(UPLOAD_FOLDER, safe_name)