from contextlib import contextmanager
from config import MYSQL_DB, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USER
import pymysql


def get_db_connection():
  """Establishes and returns a new MySQL database connection."""
  return pymysql.connect(
      host=MYSQL_HOST,
      port=MYSQL_PORT,
      user=MYSQL_USER,
      password=MYSQL_PASSWORD,
      database=MYSQL_DB,
      charset="utf8mb4",
      connect_timeout=10,
      cursorclass=pymysql.cursors.DictCursor,
  )


@contextmanager
def db_session(commit=False):
  """Context manager for automatic cursor cleanup, commit, and rollback on error.

  Usage:
      with db_session(commit=True) as cursor:
          cursor.execute("UPDATE ...")
  """
  conn = get_db_connection()
  try:
    with conn.cursor() as cursor:
      yield cursor
    if commit:
      conn.commit()
  except Exception:
    conn.rollback()
    raise
  finally:
    conn.close()


def ensure_career_roadmaps_table(cursor):
  """Ensures the career_roadmaps table exists for backwards compatibility."""
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_roadmaps (
            roadmap_id INT NOT NULL AUTO_INCREMENT,
            student_id INT NOT NULL,
            target_role VARCHAR(150) NOT NULL,
            roadmap_json JSON NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (roadmap_id),
            UNIQUE KEY uq_career_roadmaps_student_id (student_id),
            CONSTRAINT fk_career_roadmaps_student
                FOREIGN KEY (student_id) REFERENCES students(student_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)