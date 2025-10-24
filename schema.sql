CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,      -- e.g., "DBMS Normalization"
    syllabus_unit TEXT,             -- e.g., "DBMS Unit 3"
    difficulty INTEGER DEFAULT 3,   -- Scale 1 (Easy) to 5 (Hard)
    deadline DATE,                  -- For the planner
    progress_pct INTEGER DEFAULT 0  -- Revision progress
);

INSERT OR IGNORE INTO subjects (name, syllabus_unit, difficulty, deadline) VALUES 
('DBMS Normalization', 'DBMS', 4, '2025-11-01'),
('CN TCP Handshake', 'CN', 5, '2025-10-30'),
('AI Search Algorithms', 'AI', 3, '2025-11-10');