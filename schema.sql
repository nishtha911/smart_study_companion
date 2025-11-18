USE study_companion_db;

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


('DBMS', 3, 'Normalization (2NF, 3NF, BCNF)', 4, '2025-11-25', 0),
('DBMS', 4, 'ACID Properties and Serializability', 4, '2025-12-02', 0),
('DBMS', 4, 'Lock-based Concurrency Control', 5, '2025-12-09', 0),
('DBMS', 5, 'NoSQL vs RDBMS (BASE/ACID)', 3, '2025-12-16', 0),
('DBMS', 6, 'Object-Relational Mapping & Spatial Data', 3, '2025-12-23', 0),

('CN', 3, 'IP Subnetting and CIDR', 5, '2025-11-20', 0),
('CN', 3, 'Routing Protocols (OSPF, BGP)', 4, '2025-11-27', 0),
('CN', 4, 'TCP/UDP Protocols & Socket Programming', 3, '2025-12-04', 0),
('CN', 5, 'HTTP, SMTP, DNS Protocols', 2, '2025-12-11', 0),
('CN', 6, 'Medium Access Control (ALOHA, CSMA)', 3, '2025-12-18', 0),

('WT', 3, 'Servlet Life Cycle and Sessions', 3, '2025-11-18', 0),
('WT', 3, 'XML, DTD, AJAX', 2, '2025-11-25', 0),
('WT', 4, 'JSP/Servlets MVC Paradigm', 4, '2025-12-02', 0),
('WT', 5, 'PHP Scripting and MySQL', 3, '2025-12-09', 0),
('WT', 6, 'Ruby and Rails Overview', 2, '2025-12-16', 0),

('AI', 3, 'Alpha-Beta Tree Search & CSPs', 4, '2025-11-22', 0),
('AI', 4, 'First-Order Logic (FOL)', 5, '2025-11-29', 0),
('AI', 5, 'Resolution and Backward Chaining', 4, '2025-12-06', 0),
('AI', 6, 'Classical Planning Algorithms', 3, '2025-12-13', 0),

('HCI', 3, 'Interaction Styles: Direct Manipulation', 2, '2025-11-21', 0),
('HCI', 4, 'GOMS Model and Heuristic Evaluation', 3, '2025-11-28', 0),
('HCI', 5, 'Ubiquitous Computing & Hypertext', 4, '2025-12-05', 0),
('HCI', 6, 'Mobile App Navigation & Gestures', 2, '2025-12-12', 0);

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