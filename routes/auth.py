from functools import wraps
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
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '')
    gender = request.form.get('gender')
    college = request.form.get('college', '').strip()
    branch = request.form.get('branch', '').strip()
    year = request.form.get('year')

    # Basic validation
    if not full_name or not email or not password:
      return (
          render_template(
              'auth/register.html', error='Please fill in all required fields.'
          ),
          400,
      )

    conn = get_db_connection()
    try:
      with conn.cursor() as cursor:
        # Check if email is already registered
        cursor.execute(
            'SELECT student_id FROM students WHERE email = %s', (email,)
        )
        if cursor.fetchone():
          return (
              render_template(
                  'auth/register.html',
                  error='An account with this email already exists.',
              ),
              400,
          )

        # Hash password and insert record
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
                phone,
                hashed_password,
                gender,
                college,
                branch,
                year,
            ),
        )
      conn.commit()
    finally:
      conn.close()

    flash('Registration successful! Please log in.', 'success')
    return redirect(url_for('auth.login'))

  return render_template('auth/register.html')


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
              'auth/login.html', error='Please provide both email and password.'
          ),
          400,
      )

    conn = get_db_connection()
    student = None
    try:
      with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM students WHERE email = %s', (email,))
        student = cursor.fetchone()
    finally:
      conn.close()

    if student and check_password_hash(student['password'], password):
      session['student_id'] = student['student_id']
      session['student_name'] = student['full_name']
      return redirect(url_for('dashboard.dashboard_home'))

    return (
        render_template('auth/login.html', error='Invalid email or password.'),
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