CREATE TABLE IF NOT EXISTS subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject_name VARCHAR(255) NOT NULL,
    subject_unit INT DEFAULT 0,
    chapter_name TEXT NOT NULL,
    difficulty INT CHECK (difficulty BETWEEN 1 AND 5),
    deadline DATE,
    progress_pct INT DEFAULT 0 CHECK (progress_pct BETWEEN 0 AND 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_subject_chapter (subject_name, chapter_name(255))
);
INSERT IGNORE INTO subjects (subject_name, subject_unit, chapter_name, difficulty, deadline, progress_pct) VALUES
('DBMS', 3, 'Normalization', 3, '2024-12-15', 0),
('CN', 3, 'Network Layer', 4, '2024-12-10', 0),
('WT', 3, 'Java Servlets', 2, '2024-12-05', 100),
('AI', 3, 'Games', 5, '2024-12-20', 0);