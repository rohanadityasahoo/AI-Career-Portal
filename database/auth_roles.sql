-- Existing installations are upgraded automatically by ensure_auth_schema().
-- This file documents the resulting schema for manual database provisioning.

ALTER TABLE students
    ADD COLUMN IF NOT EXISTS profile_type VARCHAR(20) NOT NULL DEFAULT 'fresher'
    AFTER password,
    ADD COLUMN IF NOT EXISTS account_status VARCHAR(20) NOT NULL DEFAULT 'active'
    AFTER profile_type;

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

CREATE TABLE IF NOT EXISTS admin_activity_logs (
    activity_id BIGINT NOT NULL AUTO_INCREMENT,
    admin_id INT DEFAULT NULL,
    action VARCHAR(80) NOT NULL,
    target_type VARCHAR(40) DEFAULT NULL,
    target_id INT DEFAULT NULL,
    details VARCHAR(500) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (activity_id),
    KEY idx_admin_activity_created_at (created_at),
    KEY idx_admin_activity_admin_id (admin_id),
    CONSTRAINT fk_admin_activity_admin
        FOREIGN KEY (admin_id) REFERENCES admins(admin_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


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

ALTER TABLE professional_profile
    ADD COLUMN IF NOT EXISTS job_search_status VARCHAR(40) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS target_companies VARCHAR(300) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS employment_type VARCHAR(30) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS work_preference VARCHAR(30) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS relocation_preference VARCHAR(40) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS linkedin_url VARCHAR(255) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS portfolio_url VARCHAR(255) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS career_highlights TEXT DEFAULT NULL;
