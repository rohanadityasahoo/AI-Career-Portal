import os

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    send_from_directory
)

from werkzeug.utils import secure_filename

from database.db import get_db_connection


profile = Blueprint('profile', __name__)


# ==========================================
# PROFILE PHOTO SETTINGS
# ==========================================

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'uploads',
    'profiles'
)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}


os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):

    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ==========================================
# PROFILE PAGE
# ==========================================

@profile.route('/profile', methods=['GET', 'POST'])
def student_profile():

    if 'student_id' not in session:
        return redirect('/login')

    student_id = session['student_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # ==========================================
    # SAVE PROFILE
    # ==========================================

    if request.method == 'POST':

        # -----------------------------
        # Basic Information
        # -----------------------------

        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        gender = request.form.get('gender')

        # -----------------------------
        # Academic Information
        # -----------------------------

        college = request.form.get('college')
        branch = request.form.get('branch')
        year = request.form.get('year')

        # -----------------------------
        # Career Information
        # -----------------------------

        semester = request.form.get('semester')
        cgpa = request.form.get('cgpa')
        career_goal = request.form.get('career_goal')
        target_role = request.form.get('target_role')
        preferred_industry = request.form.get('preferred_industry')
        preferred_location = request.form.get('preferred_location')

        # -----------------------------
        # Profile Photo
        # -----------------------------

        profile_photo = request.files.get('profile_photo')

        # ==========================================
        # UPDATE STUDENTS TABLE
        # ==========================================

        cursor.execute(
            """
            update students
            set
                full_name=%s,
                phone=%s,
                gender=%s,
                college=%s,
                branch=%s,
                year=%s
            where student_id=%s
            """,
            (
                full_name,
                phone,
                gender,
                college,
                branch,
                year,
                student_id
            )
        )

        # ==========================================
        # SAVE PROFILE PHOTO
        # ==========================================

        if profile_photo and profile_photo.filename:

            if allowed_file(profile_photo.filename):

                extension = profile_photo.filename.rsplit(
                    '.', 1
                )[1].lower()

                filename = f"student_{student_id}.{extension}"

                filename = secure_filename(filename)

                # Remove previous profile photos
                for old_extension in ALLOWED_EXTENSIONS:

                    old_file = os.path.join(
                        UPLOAD_FOLDER,
                        f"student_{student_id}.{old_extension}"
                    )

                    if os.path.exists(old_file):
                        os.remove(old_file)

                # Save new photo
                photo_path = os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )

                profile_photo.save(photo_path)

                # Save filename in database
                cursor.execute(
                    """
                    update students
                    set profile_photo=%s
                    where student_id=%s
                    """,
                    (
                        filename,
                        student_id
                    )
                )

        # ==========================================
        # CHECK CAREER PROFILE
        # ==========================================

        cursor.execute(
            """
            select profile_id
            from student_profile
            where student_id=%s
            """,
            (student_id,)
        )

        existing_profile = cursor.fetchone()

        # ==========================================
        # UPDATE EXISTING CAREER PROFILE
        # ==========================================

        if existing_profile:

            cursor.execute(
                """
                update student_profile
                set
                    semester=%s,
                    cgpa=%s,
                    career_goal=%s,
                    target_role=%s,
                    preferred_industry=%s,
                    preferred_location=%s
                where student_id=%s
                """,
                (
                    semester,
                    cgpa if cgpa else None,
                    career_goal,
                    target_role,
                    preferred_industry,
                    preferred_location,
                    student_id
                )
            )

        # ==========================================
        # CREATE NEW CAREER PROFILE
        # ==========================================

        else:

            cursor.execute(
                """
                insert into student_profile
                (
                    student_id,
                    semester,
                    cgpa,
                    career_goal,
                    target_role,
                    preferred_industry,
                    preferred_location
                )
                values (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    student_id,
                    semester,
                    cgpa if cgpa else None,
                    career_goal,
                    target_role,
                    preferred_industry,
                    preferred_location
                )
            )

        # ==========================================
        # SAVE EVERYTHING
        # ==========================================

        conn.commit()

        session['student_name'] = full_name

    # ==========================================
    # GET STUDENT INFORMATION
    # ==========================================

    cursor.execute(
        """
        select
            student_id,
            full_name,
            email,
            phone,
            gender,
            college,
            branch,
            year,
            profile_photo
        from students
        where student_id=%s
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    # ==========================================
    # GET CAREER PROFILE
    # ==========================================

    cursor.execute(
        """
        select
            semester,
            cgpa,
            career_goal,
            target_role,
            preferred_industry,
            preferred_location
        from student_profile
        where student_id=%s
        """,
        (student_id,)
    )

    career_profile = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        'profile/index.html',
        student=student,
        career_profile=career_profile
    )


# ==========================================
# SERVE PROFILE PHOTO
# ==========================================

@profile.route('/profile/photo/<filename>')
def profile_photo(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )