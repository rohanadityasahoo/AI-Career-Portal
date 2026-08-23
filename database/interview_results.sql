CREATE TABLE IF NOT EXISTS interview_results (
    interview_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NULL,
    role VARCHAR(100) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    average_score DECIMAL(5, 2) NOT NULL,
    question_scores TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_interview_results_student_id (student_id)
);
