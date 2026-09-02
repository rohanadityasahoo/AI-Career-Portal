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
