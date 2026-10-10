from functools import wraps
import re
from database.db import get_db_connection
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint('auth', __name__)


def _registration_form_data():
  """Return safe, displayable registration fields without retaining passwords."""
  return {
      'full_name': request.form.get('full_name', '').strip(),
      'email': request.form.get('email', '').strip().lower(),
      'phone': request.form.get('phone', '').strip(),
      'gender': request.form.get('gender', '').strip(),
      'college': request.form.get('college', '').strip(),
      'branch': request.form.get('branch', '').strip(),
      'year': request.form.get('year', '').strip(),
  }


def _registration_error(message, form_data, status=400):
  """Re-render the form while preserving non-sensitive student details."""
  return render_template(
      'auth/register.html', error=message, form_data=form_data
  ), status


# ============================================================
# LOGIN REQUIRED DECORATOR
# ============================================================
def login_required(f):
  """Decorator to protect routes from unauthenticated access."""

  @wraps(f)
  def decorated_function(*args, **kwargs):
    if 'student_id' not in session:
      return redirect(url_for('auth.login'))
    return f(*args, **kwargs)

  return decorated_function


# ============================================================
# REGISTRATION
# ============================================================
@auth.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    form_data = _registration_form_data()
    full_name = form_data['full_name']
    email = form_data['email']
    phone = form_data['phone']
    password = request.form.get('password', '')
    password_confirmation = request.form.get('password_confirmation', '')
    gender = form_data['gender'] or None
    college = form_data['college']
    branch = form_data['branch']
    year = form_data['year']
    phone_digits = re.sub(r'\D', '', phone)

    if not full_name or not email or not phone or not password:
      return _registration_error(
          'Please complete your name, email address, phone number, and password.',
          form_data,
      )
    if len(full_name) > 100:
      return _registration_error('Please enter a name with 100 characters or fewer.', form_data)
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
      return _registration_error('Please enter a valid email address.', form_data)
    if not 7 <= len(phone_digits) <= 15:
      return _registration_error('Please enter a valid phone number with 7 to 15 digits.', form_data)
    if len(password) < 8:
      return _registration_error('Your password must contain at least 8 characters.', form_data)
    if password != password_confirmation:
      return _registration_error('The passwords do not match. Please re-enter them.', form_data)
    if gender not in {None, 'Male', 'Female', 'Other'}:
      return _registration_error('Please choose a valid gender option.', form_data)

    year_value = None
    if year:
      try:
        year_value = int(year)
      except ValueError:
        return _registration_error('Please choose a valid year of study.', form_data)
      if not 1 <= year_value <= 8:
        return _registration_error('Year of study must be between 1 and 8.', form_data)

    conn = None
    try:
      conn = get_db_connection()
      with conn.cursor() as cursor:
        # Give a helpful duplicate message before the database's unique
        # constraint has to reject the insertion.
        cursor.execute(
            'SELECT email, phone FROM students WHERE email = %s OR phone = %s',
            (email, phone_digits),
        )
        existing_student = cursor.fetchone()
        if existing_student:
          if existing_student.get('email') == email:
            return _registration_error(
                'An account with this email address already exists. Try signing in instead.',
                form_data,
            )
          return _registration_error(
              'An account with this phone number already exists. Try another number or sign in instead.',
              form_data,
          )

        hashed_password = generate_password_hash(password)
        cursor.execute(
            """
                    INSERT INTO students (
                        full_name, email, phone, password, gender, college, branch, year
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
            (
                full_name,
                email,
                phone_digits,
                hashed_password,
                gender,
                college,
                branch,
                year_value,
            ),
        )
      conn.commit()
    except Exception:
      if conn:
        conn.rollback()
      return _registration_error(
          'We could not create your account right now. Please try again shortly.',
          form_data,
          503,
      )
    finally:
      if conn:
        conn.close()

    flash('Registration successful! Please log in.', 'success')
    return redirect(url_for('auth.login'))

  return render_template('auth/register.html', form_data={})


# ============================================================
# LOGIN
# ============================================================
@auth.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not email or not password:
      return (
          render_template(
              'auth/login.html',
              error='Please provide both your email address and password.',
              email=email,
          ),
          400,
      )

    student = None
    conn = None
    try:
      conn = get_db_connection()
      with conn.cursor() as cursor:
        cursor.execute(
            'SELECT student_id, full_name, password FROM students WHERE email = %s',
            (email,),
        )
        student = cursor.fetchone()
    except Exception:
      return (
          render_template(
              'auth/login.html',
              error='We could not sign you in right now. Please try again shortly.',
              email=email,
          ),
          503,
      )
    finally:
      if conn:
        conn.close()

    if student and check_password_hash(student['password'], password):
      # Replace any anonymous or stale session data after authentication.
      session.clear()
      session['student_id'] = student['student_id']
      session['student_name'] = student['full_name']
      return redirect(url_for('dashboard.dashboard_home'))

    return (
        render_template(
            'auth/login.html',
            error='The email address or password is incorrect. Please try again.',
            email=email,
        ),
        401,
    )

  return render_template('auth/login.html')


# ============================================================
# LOGOUT
# ============================================================
@auth.route('/logout')
def logout():
  session.clear()
  flash('You have been logged out.', 'info')
  return redirect(url_for('auth.login'))
