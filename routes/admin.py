from functools import wraps

from database.db import ensure_auth_schema, get_db_connection
from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash


admin = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
  """Protect admin pages independently from student sessions."""

  @wraps(f)
  def decorated_function(*args, **kwargs):
    if 'admin_id' not in session:
      return redirect(url_for('admin.admin_login'))
    return f(*args, **kwargs)

  return decorated_function


@admin.route('/login', methods=['GET', 'POST'])
def admin_login():
  if session.get('admin_id'):
    return redirect(url_for('admin.admin_dashboard'))

  if request.method == 'POST':
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not email or not password:
      return render_template(
          'admin/login.html',
          error='Please provide both your admin email and password.',
          email=email,
      ), 400

    conn = None
    admin_account = None
    try:
      conn = get_db_connection()
      with conn.cursor() as cursor:
        ensure_auth_schema(cursor)
        conn.commit()
        cursor.execute(
            """
            SELECT admin_id, full_name, password
            FROM admins
            WHERE email = %s AND is_active = 1
            """,
            (email,),
        )
        admin_account = cursor.fetchone()
    except Exception:
      return render_template(
          'admin/login.html',
          error='Admin sign in is not available right now. Please try again shortly.',
          email=email,
      ), 503
    finally:
      if conn:
        conn.close()

    if admin_account and check_password_hash(admin_account['password'], password):
      session.clear()
      session['admin_id'] = admin_account['admin_id']
      session['admin_name'] = admin_account['full_name']
      session['account_type'] = 'admin'
      return redirect(url_for('admin.admin_dashboard'))

    return render_template(
        'admin/login.html',
        error='The admin email or password is incorrect. Please try again.',
        email=email,
    ), 401

  return render_template('admin/login.html')


@admin.route('/dashboard')
@admin_required
def admin_dashboard():
  conn = None
  stats = {'total_users': 0, 'fresher_users': 0, 'experienced_users': 0}
  users = []
  error = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      ensure_auth_schema(cursor)
      conn.commit()
      cursor.execute(
          """
          SELECT
              COUNT(*) AS total_users,
              COALESCE(SUM(profile_type = 'fresher'), 0) AS fresher_users,
              COALESCE(SUM(profile_type = 'experienced'), 0) AS experienced_users
          FROM students
          """
      )
      stats = cursor.fetchone() or stats
      cursor.execute(
          """
          SELECT student_id, full_name, email, profile_type, created_at
          FROM students
          ORDER BY created_at DESC, student_id DESC
          LIMIT 50
          """
      )
      users = cursor.fetchall() or []
  except Exception:
    error = 'We could not load the admin overview right now.'
  finally:
    if conn:
      conn.close()

  return render_template(
      'admin/dashboard.html',
      admin_name=session.get('admin_name', 'Administrator'),
      stats=stats,
      users=users,
      error=error,
  )


@admin.route('/logout')
def admin_logout():
  session.clear()
  return redirect(url_for('auth.login'))
