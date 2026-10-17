CREATE TABLE IF NOT EXISTS job_applications (
    application_id INT NOT NULL AUTO_INCREMENT,
    student_id INT NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Saved',
    priority VARCHAR(20) NOT NULL DEFAULT 'Medium',
    location VARCHAR(150) DEFAULT NULL,
    application_url VARCHAR(500) DEFAULT NULL,
    source VARCHAR(120) DEFAULT NULL,
    job_description TEXT DEFAULT NULL,
    next_action_date DATE DEFAULT NULL,
    next_action VARCHAR(500) DEFAULT NULL,
    last_contacted DATE DEFAULT NULL,
    match_score TINYINT UNSIGNED DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (application_id),
    KEY idx_job_applications_student_id (student_id),
    CONSTRAINT fk_job_applications_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;