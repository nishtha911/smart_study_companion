USE study_companion_db;

CREATE TABLE IF NOT EXISTS subjects (
	id INT PRIMARY KEY AUTO_INCREMENT,
	subject_name VARCHAR(255) NOT NULL,
    subject_unit INT NOT NULL,
    chapter_name TEXT NOT NULL,
    topic_name TEXT,
    difficulty INT CHECK (difficulty BETWEEN 1 AND 5),
    deadline DATE,
    progress_pct INT DEFAULT 0 CHECK (progress_pct BETWEEN 0 AND 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_subject_chapter (subject_name, chapter_name(255))
);


INSERT IGNORE INTO subjects (subject_name, subject_unit, chapter_name, topic_name, difficulty, deadline, progress_pct) VALUES
('DBMS', 3, 'Relational Database Design ', 'Relational Model', 3, '2025-11-20', 0),
('DBMS', 4, 'Database Transaction Management', 'ACID Properties and Serializability', 4, '2025-11-20', 0),
('DBMS', 5, 'NoSQL Databases', 'Distributed Database System', 3, '2025-11-20', 0),
('DBMS', 6, 'Advances in Databases', 'Emerging Databases', 3, '2025-11-21', 0),

('CN', 3, 'Network Layer', 'Introduction and Switching Techniques', 1, '2025-11-21', 0),
('CN', 4, 'Transport Layer', 'P2P Delivery and Socket Programming', 3, '2025-11-21', 0),
('CN', 5, 'Application Layer', 'Client Server Paradigm', 2, '2025-12-22', 0),
('CN', 6, 'Medium Access Control', 'Channel Allocation', 3, '2025-12-22', 0),

('WT', 3, 'Java Servlets and XML ', 'Servlets', 2, '2025-11-22', 0),
('WT', 4, 'JSP and Web Services', 'Introduction to JSP', 2, '2025-12-23', 0),
('WT', 5, 'Server Side Scripting Languages ', 'Introduction to PHP', 2, '2025-12-23', 0),
('WT', 6, 'Ruby and Rails', 'Ruby Overview', 2, '2025-12-23', 0),

('AI', 3, 'Adversarial Search and Games', 'Game Theory', 2, '2025-11-28', 0),
('AI', 4, 'Knowledge', 'Logical Agents', 2, '2025-11-28', 0),
('AI', 5, 'Reasoning', 'Inference in FOL', 4, '2025-12-29', 0),
('AI', 6, 'Planning', 'Types of Planning', 3, '2025-12-29', 0),

('HCI', 3, 'Interaction Styles and HCI in Software Process', 'Direct Manipulation', 2, '2025-11-30', 0),
('HCI', 4, 'Usability Evaluation and Universal Design', 'User interface design process', 2, '2025-11-30', 0),
('HCI', 5, 'HCI Paradigms', 'Paradigms for Interaction', 4, '2025-12-1', 0),
('HCI', 6, 'HCI for Mobile and Handheld devices', 'Mobile App Navigation & Gestures', 2, '2025-12-1', 0);

CREATE TABLE IF NOT EXISTS exams (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject_name VARCHAR(255) NOT NULL,
    exam_type ENUM('Class Test', 'InSem', 'EndSem') NOT NULL,
    exam_date DATE NOT NULL
);

INSERT IGNORE INTO exams (subject_name, exam_type, exam_date) VALUES
('DBMS', 'EndSem', '2025-12-11'),
('CN', 'EndSem', '2025-12-13'),
('WT', 'EndSem', '2025-12-16'),
('AI', 'EndSem', '2025-12-18'),
('HCI', 'EndSem', '2025-12-20');