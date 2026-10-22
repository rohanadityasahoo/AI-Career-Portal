from functools import wraps
import os

from ai_modules.career_ai import is_configured
from database.db import ensure_auth_schema, get_db_connection
from database.db import AI_FEATURE_DEFINITIONS
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash


admin = Blueprint('admin', __name__, url_prefix='/admin')

PROFILE_TYPES = {'fresher', 'experienced'}
ACCOUNT_STATUSES = {'active', 'suspended'}
AI_FEATURE_KEYS = dict(AI_FEATURE_DEFINITIONS)


def admin_required(f):
  """Protect admin pages independently from student sessions."""

  @wraps(f)
  def decorated_function(*args, **kwargs):
    if 'admin_id' not in session:
      return redirect(url_for('admin.admin_login'))
    return f(*args, **kwargs)

  return decorated_function


def _record_activity_cursor(
    cursor,
    action,
    target_type=None,
    target_id=None,
    details=None,
    admin_id=None,
):
  cursor.execute(
      """
      INSERT INTO admin_activity_logs
          (admin_id, action, target_type, target_id, details)
      VALUES (%s, %s, %s, %s, %s)
      """,
      (
          admin_id if admin_id is not None else session.get('admin_id'),
          action,
          target_type,
          target_id,
          details,
      ),
  )


def _record_activity(
    action,
    target_type=None,
    target_id=None,
    details=None,
    admin_id=None,
):
  """Write an audit event without blocking the action that triggered it."""
  conn = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      ensure_auth_schema(cursor)
      _record_activity_cursor(
          cursor,
          action,
          target_type=target_type,
          target_id=target_id,
          details=details,
          admin_id=admin_id,
      )
    conn.commit()
  except Exception:
    if conn:
      conn.rollback()
  finally:
    if conn:
      conn.close()


def _user_filters():
  search = request.args.get('search', '').strip()
  profile_type = request.args.get('profile_type', '').strip().lower()
  account_status = request.args.get('account_status', '').strip().lower()
  if profile_type not in PROFILE_TYPES:
    profile_type = ''
  if account_status not in ACCOUNT_STATUSES:
    account_status = ''
  return search, profile_type, account_status


@admin.route('', methods=['GET'])
@admin.route('/', methods=['GET'])
def admin_index():
  if session.get('admin_id'):
    return redirect(url_for('admin.admin_dashboard'))
  return redirect(url_for('admin.admin_login'))


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
      _record_activity(
          'admin_login',
          target_type='admin',
          target_id=admin_account['admin_id'],
          details='Administrator signed in.',
          admin_id=admin_account['admin_id'],
      )
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
  stats = {
      'total_users': 0,
      'active_users': 0,
      'suspended_users': 0,
      'new_users': 0,
      'fresher_users': 0,
      'experienced_users': 0,
      'resume_analyses': 0,
      'interviews': 0,
  }
  users = []
  activities = []
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
              COALESCE(SUM(account_status = 'active'), 0) AS active_users,
              COALESCE(SUM(account_status = 'suspended'), 0) AS suspended_users,
              COALESCE(SUM(created_at >= DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 7 DAY)), 0) AS new_users,
              COALESCE(SUM(account_status = 'active' AND profile_type = 'fresher'), 0) AS fresher_users,
              COALESCE(SUM(account_status = 'active' AND profile_type = 'experienced'), 0) AS experienced_users
          FROM students
          """
      )
      stats.update(cursor.fetchone() or {})
      cursor.execute('SELECT COUNT(*) AS count FROM resume_analysis')
      stats['resume_analyses'] = (cursor.fetchone() or {}).get('count', 0)
      cursor.execute('SELECT COUNT(*) AS count FROM interview_results')
      stats['interviews'] = (cursor.fetchone() or {}).get('count', 0)
      cursor.execute(
          """
          SELECT student_id, full_name, email, profile_type, account_status, created_at
          FROM students
          ORDER BY created_at DESC, student_id DESC
          LIMIT 8
          """
      )
      users = cursor.fetchall() or []
      cursor.execute(
          """
          SELECT activity_id, action, target_type, target_id, details, created_at
          FROM admin_activity_logs
          ORDER BY created_at DESC, activity_id DESC
          LIMIT 8
          """
      )
      activities = cursor.fetchall() or []
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
      activities=activities,
      error=error,
  )


@admin.route('/ai')
@admin_required
def ai_management():
  conn = None
  stats = {
      'total_requests': 0,
      'successful_requests': 0,
      'failed_requests': 0,
      'disabled_requests': 0,
      'not_configured_requests': 0,
      'last_24_hours': 0,
      'success_rate': 0,
  }
  features = []
  recent_logs = []
  error = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      ensure_auth_schema(cursor)
      conn.commit()
      cursor.execute(
          """
          SELECT
              COUNT(*) AS total_requests,
              COALESCE(SUM(status = 'success'), 0) AS successful_requests,
              COALESCE(SUM(status = 'error'), 0) AS failed_requests,
              COALESCE(SUM(status = 'disabled'), 0) AS disabled_requests,
              COALESCE(SUM(status = 'not_configured'), 0) AS not_configured_requests,
              COALESCE(SUM(created_at >= DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 24 HOUR)), 0) AS last_24_hours
          FROM ai_usage_logs
          """
      )
      stats.update(cursor.fetchone() or {})
      if stats['total_requests']:
        stats['success_rate'] = round(
            stats['successful_requests'] * 100 / stats['total_requests']
        )
      cursor.execute(
          """
          SELECT flags.feature_key, flags.label, flags.is_enabled,
                 COUNT(logs.request_id) AS total_requests,
                 COALESCE(SUM(logs.status = 'success'), 0) AS successful_requests,
                 COALESCE(SUM(logs.status = 'error'), 0) AS failed_requests,
                 MAX(logs.created_at) AS last_used
          FROM ai_feature_flags AS flags
          LEFT JOIN ai_usage_logs AS logs
              ON logs.feature_key = flags.feature_key
          GROUP BY flags.feature_key, flags.label, flags.is_enabled
          ORDER BY flags.label
          """
      )
      features = cursor.fetchall() or []
      cursor.execute(
          """
          SELECT logs.feature_key, flags.label, logs.model, logs.status,
                 logs.latency_ms, logs.error_code, logs.created_at
          FROM ai_usage_logs AS logs
          LEFT JOIN ai_feature_flags AS flags
              ON flags.feature_key = logs.feature_key
          ORDER BY logs.created_at DESC, logs.request_id DESC
          LIMIT 40
          """
      )
      recent_logs = cursor.fetchall() or []
  except Exception:
    error = 'We could not load AI management data right now.'
  finally:
    if conn:
      conn.close()

  return render_template(
      'admin/ai.html',
      ai_configured=is_configured(),
      ai_model=os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b').strip()
      or 'openai/gpt-oss-20b',
      enabled_features=sum(1 for feature in features if feature['is_enabled']),
      feature_count=len(features),
      stats=stats,
      features=features,
      recent_logs=recent_logs,
      error=error,
  )


@admin.post('/ai/features/<feature_key>')
@admin_required
def update_ai_feature(feature_key):
  if feature_key not in AI_FEATURE_KEYS:
    abort(404)
  is_enabled = request.form.get('is_enabled') == '1'
  conn = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      ensure_auth_schema(cursor)
      cursor.execute(
          'UPDATE ai_feature_flags SET is_enabled = %s WHERE feature_key = %s',
          (1 if is_enabled else 0, feature_key),
      )
      _record_activity_cursor(
          cursor,
          'ai_feature_enabled' if is_enabled else 'ai_feature_disabled',
          target_type='ai_feature',
          details=f"{AI_FEATURE_KEYS[feature_key]} {'enabled' if is_enabled else 'disabled'}.",
      )
    conn.commit()
    flash(
        f"{AI_FEATURE_KEYS[feature_key]} {'enabled' if is_enabled else 'disabled'}.",
        'success',
    )
  except Exception:
    if conn:
      conn.rollback()
    flash('We could not update that AI feature right now.', 'danger')
  finally:
    if conn:
      conn.close()
  return redirect(url_for('admin.ai_management'))


@admin.route('/users')
@admin_required
def admin_users():
  search, profile_type, account_status = _user_filters()
  conn = None
  users = []
  error = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      ensure_auth_schema(cursor)
      conn.commit()
      conditions = []
      parameters = []
      if search:
        conditions.append('(full_name LIKE %s OR email LIKE %s OR phone LIKE %s)')
        search_value = f'%{search}%'
        parameters.extend([search_value, search_value, search_value])
      if profile_type:
        conditions.append('profile_type = %s')
        parameters.append(profile_type)
      if account_status:
        conditions.append('account_status = %s')
        parameters.append(account_status)
      where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ''
      cursor.execute(
          f"""
          SELECT student_id, full_name, email, phone, profile_type,
                 account_status, college, branch, created_at
          FROM students
          {where_clause}
          ORDER BY created_at DESC, student_id DESC
          LIMIT 100
          """,
          tuple(parameters),
      )
      users = cursor.fetchall() or []
  except Exception:
    error = 'We could not load the user directory right now.'
  finally:
    if conn:
      conn.close()

  return render_template(
      'admin/users.html',
      users=users,
      search=search,
      profile_type=profile_type,
      account_status=account_status,
      error=error,
  )


@admin.route('/users/<int:student_id>')
@admin_required
def admin_user_detail(student_id):
  conn = None
  user = None
  usage = {'resume_count': 0, 'interview_count': 0}
  recent_activity = []
  error = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      ensure_auth_schema(cursor)
      conn.commit()
      cursor.execute(
          """
          SELECT student_id, full_name, email, phone, profile_type,
                 account_status, gender, college, branch, year,
                 profile_photo, created_at
          FROM students
          WHERE student_id = %s
          """,
          (student_id,),
      )
      user = cursor.fetchone()
      if not user:
        abort(404)
      cursor.execute(
          """
          SELECT COUNT(*) AS resume_count
          FROM resume_analysis
          WHERE student_id = %s
          """,
          (student_id,),
      )
      usage.update(cursor.fetchone() or {})
      cursor.execute(
          """
          SELECT COUNT(*) AS interview_count
          FROM interview_results
          WHERE student_id = %s
          """,
          (student_id,),
      )
      usage.update(cursor.fetchone() or {})
      cursor.execute(
          """
          SELECT action, details, created_at
          FROM admin_activity_logs
          WHERE target_type = 'user' AND target_id = %s
          ORDER BY created_at DESC, activity_id DESC
          LIMIT 10
          """,
          (student_id,),
      )
      recent_activity = cursor.fetchall() or []
  except HTTPException:
    raise
  except Exception:
    error = 'We could not load this user right now.'
  finally:
    if conn:
      conn.close()

  if not user:
    return render_template('admin/user_detail.html', error=error), 404
  return render_template(
      'admin/user_detail.html',
      user=user,
      usage=usage,
      recent_activity=recent_activity,
      error=error,
  )


@admin.post('/users/<int:student_id>/status')
@admin_required
def update_user_status(student_id):
  new_status = request.form.get('account_status', '').strip().lower()
  if new_status not in ACCOUNT_STATUSES:
    flash('Choose a valid account status.', 'danger')
    return redirect(url_for('admin.admin_user_detail', student_id=student_id))

  conn = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      ensure_auth_schema(cursor)
      cursor.execute(
          'SELECT full_name, email FROM students WHERE student_id = %s',
          (student_id,),
      )
      user = cursor.fetchone()
      if not user:
        abort(404)
      cursor.execute(
          'UPDATE students SET account_status = %s WHERE student_id = %s',
          (new_status, student_id),
      )
      action = 'user_suspended' if new_status == 'suspended' else 'user_reactivated'
      _record_activity_cursor(
          cursor,
          action,
          target_type='user',
          target_id=student_id,
          details=f"{user['full_name']} ({user['email']}) marked {new_status}.",
      )
    conn.commit()
    flash(f"{user['full_name']} is now {new_status}.", 'success')
  except HTTPException:
    raise
  except Exception:
    if conn:
      conn.rollback()
    flash('We could not update this user account right now.', 'danger')
  finally:
    if conn:
      conn.close()
  return redirect(url_for('admin.admin_user_detail', student_id=student_id))


@admin.route('/activity')
@admin_required
def admin_activity():
  conn = None
  activities = []
  error = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      ensure_auth_schema(cursor)
      conn.commit()
      cursor.execute(
          """
          SELECT admin_activity_logs.activity_id, admin_activity_logs.action,
                 admin_activity_logs.target_type, admin_activity_logs.target_id,
                 admin_activity_logs.details, admin_activity_logs.created_at,
                 COALESCE(admins.full_name, 'System') AS admin_name
          FROM admin_activity_logs
          LEFT JOIN admins ON admins.admin_id = admin_activity_logs.admin_id
          ORDER BY admin_activity_logs.created_at DESC, activity_id DESC
          LIMIT 100
          """
      )
      activities = cursor.fetchall() or []
  except Exception:
    error = 'We could not load the activity history right now.'
  finally:
    if conn:
      conn.close()
  return render_template('admin/activity.html', activities=activities, error=error)


@admin.route('/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
  error = None
  profile = {
      'full_name': session.get('admin_name', 'Administrator'),
      'email': '',
  }
  conn = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      ensure_auth_schema(cursor)
      conn.commit()
      cursor.execute(
          'SELECT full_name, email, password FROM admins WHERE admin_id = %s',
          (session['admin_id'],),
      )
      account = cursor.fetchone()
      if not account:
        session.clear()
        return redirect(url_for('admin.admin_login'))
      profile.update({key: account[key] for key in ('full_name', 'email')})

      if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        if not check_password_hash(account['password'], current_password):
          error = 'Your current password is incorrect.'
        elif len(new_password) < 8:
          error = 'Your new password must contain at least 8 characters.'
        elif new_password != confirm_password:
          error = 'The new password confirmation does not match.'
        else:
          cursor.execute(
              'UPDATE admins SET password = %s WHERE admin_id = %s',
              (generate_password_hash(new_password), session['admin_id']),
          )
          _record_activity_cursor(
              cursor,
              'admin_password_changed',
              target_type='admin',
              target_id=session['admin_id'],
              details='Administrator password changed.',
          )
          conn.commit()
          flash('Your admin password has been changed.', 'success')
          return redirect(url_for('admin.admin_settings'))
  except Exception:
    if conn:
      conn.rollback()
    error = error or 'We could not load or update admin settings right now.'
  finally:
    if conn:
      conn.close()
  return render_template('admin/settings.html', profile=profile, error=error)


@admin.route('/logout')
def admin_logout():
  if session.get('admin_id'):
    _record_activity(
        'admin_logout',
        target_type='admin',
        target_id=session.get('admin_id'),
        details='Administrator signed out.',
    )
  session.clear()
  return redirect(url_for('admin.admin_login'))
