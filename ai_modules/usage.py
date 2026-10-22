"""Small, privacy-preserving helpers for AI feature controls and telemetry."""

import os
from contextlib import contextmanager
from contextvars import ContextVar
from time import perf_counter

from database.db import get_db_connection


_AI_CONTEXT = ContextVar(
    'ai_context',
    default={'feature_key': 'unknown', 'student_id': None},
)


@contextmanager
def ai_feature_context(feature_key, student_id=None):
  token = _AI_CONTEXT.set({
      'feature_key': feature_key,
      'student_id': student_id,
  })
  try:
    yield
  finally:
    _AI_CONTEXT.reset(token)


def current_ai_context():
  return dict(_AI_CONTEXT.get())


def _elapsed_ms(started_at):
  return max(0, int((perf_counter() - started_at) * 1000))


def is_ai_feature_enabled(feature_key):
  if not feature_key or feature_key == 'unknown':
    return True
  conn = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      cursor.execute(
          'SELECT is_enabled FROM ai_feature_flags WHERE feature_key = %s',
          (feature_key,),
      )
      row = cursor.fetchone()
      return row is None or bool(row['is_enabled'])
  except Exception:
    return True
  finally:
    if conn:
      conn.close()


def log_ai_request(started_at, status, error_code=None):
  """Store request metadata only; never store prompts, responses, or secrets."""
  context = current_ai_context()
  conn = None
  try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
      cursor.execute(
          """
          INSERT INTO ai_usage_logs
              (feature_key, student_id, model, status, latency_ms, error_code)
          VALUES (%s, %s, %s, %s, %s, %s)
          """,
          (
              context.get('feature_key') or 'unknown',
              context.get('student_id'),
              os.getenv('GROQ_MODEL', '').strip() or None,
              status,
              _elapsed_ms(started_at),
              error_code,
          ),
      )
    conn.commit()
  except Exception:
    if conn:
      conn.rollback()
  finally:
    if conn:
      conn.close()
