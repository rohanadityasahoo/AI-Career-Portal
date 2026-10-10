import hmac
import os
import re
import secrets
import uuid
from decimal import Decimal, InvalidOperation

from database.db import get_db_connection
from flask import (
    Blueprint,
    abort,
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
MAX_PROFILE_PHOTO_BYTES = 5 * 1024 * 1024
CSRF_TOKEN_KEY = 'profile_form_csrf_token'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def _compact_text(value):
  """Trim a submitted text value while avoiding accidental extra spacing."""
  return ' '.join((value or '').strip().split())


def _profile_form_data():
  """Return only the editable profile data submitted by the student."""
  return {
      'full_name': _compact_text(request.form.get('full_name')),
      'phone': _compact_text(request.form.get('phone')),
      'gender': request.form.get('gender', '').strip(),
      'college': _compact_text(request.form.get('college')),
      'branch': _compact_text(request.form.get('branch')),
      'year': request.form.get('year', '').strip(),
      'semester': _compact_text(request.form.get('semester')),
      'cgpa': request.form.get('cgpa', '').strip(),
      'career_goal': _compact_text(request.form.get('career_goal')),
      'target_role': _compact_text(request.form.get('target_role')),
      'preferred_industry': _compact_text(
          request.form.get('preferred_industry')
      ),
      'preferred_location': _compact_text(
          request.form.get('preferred_location')
      ),
  }


def _validate_profile_data(form_data):
  """Validate and normalise profile values before a database update."""
  if not form_data['full_name']:
    return None, 'Please enter your full name.'
  if len(form_data['full_name']) > 100:
    return None, 'Your full name must be 100 characters or fewer.'

  phone_digits = re.sub(r'\D', '', form_data['phone'])
  if not 7 <= len(phone_digits) <= 15:
    return None, 'Please enter a phone number with 7 to 15 digits.'

  gender = form_data['gender'] or None
  if gender not in {None, 'Male', 'Female', 'Other'}:
    return None, 'Please choose a valid gender option.'

  field_limits = {
      'college': (150, 'College or university'),
      'branch': (100, 'Branch or course'),
      'semester': (30, 'Current semester'),
      'career_goal': (150, 'Career goal'),
      'target_role': (150, 'Target job role'),
      'preferred_industry': (150, 'Preferred industry'),
      'preferred_location': (150, 'Preferred work location'),
  }
  for field, (limit, label) in field_limits.items():
    if len(form_data[field]) > limit:
      return None, f'{label} must be {limit} characters or fewer.'

  year = None
  if form_data['year']:
    try:
      year = int(form_data['year'])
    except ValueError:
      return None, 'Please choose a valid year of study.'
    if not 1 <= year <= 8:
      return None, 'Year of study must be between 1 and 8.'

  cgpa = None
  if form_data['cgpa']:
    try:
      cgpa = Decimal(form_data['cgpa'])
    except InvalidOperation:
      return None, 'Please enter a valid CGPA.'
    if not Decimal('0') <= cgpa <= Decimal('10'):
      return None, 'CGPA must be between 0.00 and 10.00.'

  validated_data = {
      **form_data,
      'phone': phone_digits,
      'gender': gender,
      'year': year,
      'cgpa': cgpa,
  }
  return validated_data, None


def _validate_profile_photo(photo):
  """Accept a small JPG or PNG only when its file signature matches."""
  if not photo or not photo.filename:
    return None, None

  if '.' not in photo.filename:
    return None, 'Choose a JPG or PNG profile photo.'

  extension = photo.filename.rsplit('.', 1)[1].lower()
  if extension not in ALLOWED_EXTENSIONS:
    return None, 'Profile photos must be JPG, JPEG, or PNG files.'

  stream = photo.stream
  stream.seek(0, os.SEEK_END)
  size = stream.tell()
  stream.seek(0)
  if size > MAX_PROFILE_PHOTO_BYTES:
    return None, 'Profile photos must be 5 MB or smaller.'

  signature = stream.read(8)
  stream.seek(0)
  is_jpeg = signature.startswith(b'\xff\xd8\xff')
  is_png = signature == b'\x89PNG\r\n\x1a\n'
  if extension in {'jpg', 'jpeg'} and not is_jpeg:
    return None, 'That file does not appear to be a valid JPG image.'
  if extension == 'png' and not is_png:
    return None, 'That file does not appear to be a valid PNG image.'

  return extension, None


def _load_profile(student_id):
  """Fetch the account and optional career details for the signed-in student."""
  conn = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      cursor.execute(
          """
              SELECT student_id, full_name, email, phone, gender, college,
                     branch, year, profile_photo
              FROM students
              WHERE student_id=%s
              """,
          (student_id,),
      )
      student = cursor.fetchone()
      cursor.execute(
          """
              SELECT semester, cgpa, career_goal, target_role,
                     preferred_industry, preferred_location
              FROM student_profile
              WHERE student_id=%s
              """,
          (student_id,),
      )
      career_profile = cursor.fetchone()
      return student, career_profile
  finally:
    if conn:
      conn.close()


def _profile_completion(student, career_profile):
  """Calculate a useful, transparent profile-completion score."""
  tracked_values = (
      student.get('full_name'),
      student.get('phone'),
      student.get('gender'),
      student.get('college'),
      student.get('branch'),
      student.get('year'),
      career_profile.get('semester'),
      career_profile.get('cgpa'),
      career_profile.get('career_goal'),
      career_profile.get('target_role'),
      career_profile.get('preferred_industry'),
      career_profile.get('preferred_location'),
  )
  completed_fields = sum(value is not None and value != '' for value in tracked_values)
  total_fields = len(tracked_values)
  return round(100 * completed_fields / total_fields), completed_fields, total_fields


def _profile_csrf_token():
  token = session.get(CSRF_TOKEN_KEY)
  if not token:
    token = secrets.token_urlsafe(32)
    session[CSRF_TOKEN_KEY] = token
  return token


def _render_profile(student, career_profile, error=None, status=200):
  student = student or {}
  career_profile = career_profile or {}
  completion, completed_fields, total_fields = _profile_completion(
      student, career_profile
  )
  return render_template(
      'profile/index.html',
      student=student,
      career_profile=career_profile,
      profile_completion=completion,
      completed_fields=completed_fields,
      total_profile_fields=total_fields,
      csrf_token=_profile_csrf_token(),
      error=error,
  ), status


def _submitted_profile_display(student, career_profile, form_data):
  """Keep safe submitted values visible when validation needs correction."""
  display_student = {
      **student,
      'full_name': form_data['full_name'],
      'phone': form_data['phone'],
      'gender': form_data['gender'],
      'college': form_data['college'],
      'branch': form_data['branch'],
      'year': form_data['year'],
  }
  display_career_profile = {
      **career_profile,
      'semester': form_data['semester'],
      'cgpa': form_data['cgpa'],
      'career_goal': form_data['career_goal'],
      'target_role': form_data['target_role'],
      'preferred_industry': form_data['preferred_industry'],
      'preferred_location': form_data['preferred_location'],
  }
  return display_student, display_career_profile


# ==========================================
# PROFILE PAGE
# ==========================================


@profile.route('/profile', methods=['GET', 'POST'])
@login_required
def student_profile():
  student_id = session['student_id']
  try:
    student, career_profile = _load_profile(student_id)
  except Exception:
    return _render_profile(
        {}, {}, 'We could not load your profile right now. Please try again shortly.', 503
    )

  if not student:
    session.clear()
    return redirect(url_for('auth.login'))

  career_profile = career_profile or {}
  if request.method == 'GET':
    return _render_profile(student, career_profile)

  form_data = _profile_form_data()
  display_student, display_career_profile = _submitted_profile_display(
      student, career_profile, form_data
  )

  submitted_token = request.form.get('csrf_token', '')
  if not submitted_token or not hmac.compare_digest(
      submitted_token, _profile_csrf_token()
  ):
    return _render_profile(
        display_student,
        display_career_profile,
        'Your form session expired. Please refresh the page and try again.',
        400,
    )

  validated_data, validation_error = _validate_profile_data(form_data)
  if validation_error:
    return _render_profile(
        display_student, display_career_profile, validation_error, 400
    )

  photo = request.files.get('profile_photo')
  photo_extension, photo_error = _validate_profile_photo(photo)
  if photo_error:
    return _render_profile(
        display_student, display_career_profile, photo_error, 400
    )

  new_photo_filename = None
  new_photo_path = None
  old_photo_filename = student.get('profile_photo')
  conn = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      cursor.execute(
          'SELECT student_id FROM students WHERE phone=%s AND student_id != %s',
          (validated_data['phone'], student_id),
      )
      if cursor.fetchone():
        conn.rollback()
        return _render_profile(
            display_student,
            display_career_profile,
            'That phone number is already connected to another account.',
            409,
        )

      if photo_extension:
        new_photo_filename = (
            f'student_{student_id}_{uuid.uuid4().hex}.{photo_extension}'
        )
        new_photo_path = os.path.join(UPLOAD_FOLDER, new_photo_filename)
        photo.save(new_photo_path)

      cursor.execute(
          """
              UPDATE students
              SET full_name=%s, phone=%s, gender=%s, college=%s, branch=%s,
                  year=%s, profile_photo=COALESCE(%s, profile_photo)
              WHERE student_id=%s
              """,
          (
              validated_data['full_name'],
              validated_data['phone'],
              validated_data['gender'],
              validated_data['college'] or None,
              validated_data['branch'] or None,
              validated_data['year'],
              new_photo_filename,
              student_id,
          ),
      )
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
              validated_data['semester'] or None,
              validated_data['cgpa'],
              validated_data['career_goal'] or None,
              validated_data['target_role'] or None,
              validated_data['preferred_industry'] or None,
              validated_data['preferred_location'] or None,
          ),
      )
    conn.commit()
  except Exception:
    if conn:
      conn.rollback()
    if new_photo_path and os.path.exists(new_photo_path):
      os.remove(new_photo_path)
    return _render_profile(
        display_student,
        display_career_profile,
        'We could not save your changes right now. Please try again shortly.',
        503,
    )
  finally:
    if conn:
      conn.close()

  if new_photo_filename and old_photo_filename:
    old_photo_path = os.path.join(
        UPLOAD_FOLDER, secure_filename(old_photo_filename)
    )
    if os.path.exists(old_photo_path):
      os.remove(old_photo_path)

  session['student_name'] = validated_data['full_name']
  flash('Your profile has been saved.', 'success')
  return redirect(url_for('profile.student_profile'))


# ==========================================
# SERVE PROFILE PHOTO
# ==========================================


@profile.route('/profile/photo/<filename>')
@login_required
def profile_photo(filename):
  safe_name = secure_filename(filename)
  if safe_name != filename:
    abort(404)

  conn = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      cursor.execute(
          'SELECT profile_photo FROM students WHERE student_id=%s',
          (session['student_id'],),
      )
      student = cursor.fetchone()
  finally:
    if conn:
      conn.close()

  if not student or student.get('profile_photo') != safe_name:
    abort(404)
  return send_from_directory(UPLOAD_FOLDER, safe_name)
