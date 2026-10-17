from contextlib import contextmanager
from config import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    ADMIN_PASSWORD_HASH,
    MYSQL_DB,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
)
import pymysql
from werkzeug.security import generate_password_hash


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


def ensure_auth_schema(cursor):
  """Keep role and admin tables available for existing installations."""
  cursor.execute(
      """
      SELECT COUNT(*) AS column_count
      FROM information_schema.columns
      WHERE table_schema = DATABASE()
        AND table_name = 'students'
        AND column_name = 'profile_type'
      """
  )
  profile_type_column = cursor.fetchone() or {}
  if not int(profile_type_column.get('column_count') or 0):
    cursor.execute(
        """
        ALTER TABLE students
        ADD COLUMN profile_type VARCHAR(20) NOT NULL DEFAULT 'fresher'
        AFTER password
        """
    )

  cursor.execute(
      """
      CREATE TABLE IF NOT EXISTS admins (
          admin_id INT NOT NULL AUTO_INCREMENT,
          full_name VARCHAR(100) NOT NULL,
          email VARCHAR(100) NOT NULL,
          password VARCHAR(255) NOT NULL,
          is_active TINYINT(1) NOT NULL DEFAULT 1,
          created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (admin_id),
          UNIQUE KEY uq_admins_email (email)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
      """
  )

  cursor.execute(
      """
      CREATE TABLE IF NOT EXISTS professional_profile (
          profile_id INT NOT NULL AUTO_INCREMENT,
          student_id INT NOT NULL,
          current_job_title VARCHAR(150) DEFAULT NULL,
          current_company VARCHAR(150) DEFAULT NULL,
          years_experience DECIMAL(4,1) DEFAULT NULL,
          current_industry VARCHAR(150) DEFAULT NULL,
          key_skills TEXT DEFAULT NULL,
          target_field VARCHAR(150) DEFAULT NULL,
          target_role VARCHAR(150) DEFAULT NULL,
          career_switch_reason VARCHAR(500) DEFAULT NULL,
          notice_period VARCHAR(60) DEFAULT NULL,
          expected_salary VARCHAR(100) DEFAULT NULL,
          preferred_location VARCHAR(150) DEFAULT NULL,
          job_search_status VARCHAR(40) DEFAULT NULL,
          target_companies VARCHAR(300) DEFAULT NULL,
          employment_type VARCHAR(30) DEFAULT NULL,
          work_preference VARCHAR(30) DEFAULT NULL,
          relocation_preference VARCHAR(40) DEFAULT NULL,
          linkedin_url VARCHAR(255) DEFAULT NULL,
          portfolio_url VARCHAR(255) DEFAULT NULL,
          career_highlights TEXT DEFAULT NULL,
          created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
              ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (profile_id),
          UNIQUE KEY uq_professional_profile_student_id (student_id),
          CONSTRAINT fk_professional_profile_student
              FOREIGN KEY (student_id) REFERENCES students(student_id)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
      """
  )

  cursor.execute(
      """
      SELECT column_name AS column_name
      FROM information_schema.columns
      WHERE table_schema = DATABASE()
        AND table_name = 'professional_profile'
      """
  )
  existing_profile_columns = {
      row['column_name'] for row in cursor.fetchall()
  }
  profile_columns = {
      'job_search_status': 'VARCHAR(40) DEFAULT NULL',
      'target_companies': 'VARCHAR(300) DEFAULT NULL',
      'employment_type': 'VARCHAR(30) DEFAULT NULL',
      'work_preference': 'VARCHAR(30) DEFAULT NULL',
      'relocation_preference': 'VARCHAR(40) DEFAULT NULL',
      'linkedin_url': 'VARCHAR(255) DEFAULT NULL',
      'portfolio_url': 'VARCHAR(255) DEFAULT NULL',
      'career_highlights': 'TEXT DEFAULT NULL',
  }
  for column_name, definition in profile_columns.items():
    if column_name not in existing_profile_columns:
      cursor.execute(
          'ALTER TABLE professional_profile ADD COLUMN ' + column_name + ' ' + definition
      )

  if ADMIN_EMAIL and (ADMIN_PASSWORD_HASH or ADMIN_PASSWORD):
    cursor.execute(
        'SELECT admin_id FROM admins WHERE email = %s',
        (ADMIN_EMAIL,),
    )
    if not cursor.fetchone():
      cursor.execute(
          """
          INSERT INTO admins (full_name, email, password)
          VALUES (%s, %s, %s)
          """,
          (
              'CareerPilot Administrator',
              ADMIN_EMAIL,
              ADMIN_PASSWORD_HASH or generate_password_hash(ADMIN_PASSWORD),
          ),
      )
