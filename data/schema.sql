-- Database schema for Neurologix Smart Search POV
-- MySQL/MariaDB compatible
-- @mode mysql

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    team_id VARCHAR(50) NOT NULL,
    age INT,
    position VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_team_id (team_id),
    INDEX idx_name (name)
);

-- Symptom assessments table
CREATE TABLE IF NOT EXISTS symptom_assessments (
    symptom_id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    headache_severity INT DEFAULT 0 CHECK (headache_severity >= 0 AND headache_severity <= 6),
    nausea_severity INT DEFAULT 0 CHECK (nausea_severity >= 0 AND nausea_severity <= 6),
    dizziness_severity INT DEFAULT 0 CHECK (dizziness_severity >= 0 AND dizziness_severity <= 6),
    confusion_severity INT DEFAULT 0 CHECK (confusion_severity >= 0 AND confusion_severity <= 6),
    memory_problems_severity INT DEFAULT 0 CHECK (memory_problems_severity >= 0 AND memory_problems_severity <= 6),
    emotional_symptoms_severity INT DEFAULT 0 CHECK (emotional_symptoms_severity >= 0 AND emotional_symptoms_severity <= 6),
    total_symptom_score INT DEFAULT 0 CHECK (total_symptom_score >= 0 AND total_symptom_score <= 132),
    assessment_type ENUM('baseline', 'post_injury', 'symptom_checklist') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_date (patient_id, assessment_date),
    INDEX idx_assessment_date (assessment_date),
    INDEX idx_assessment_type (assessment_type),
    INDEX idx_total_score (total_symptom_score)
);

-- Reaction time tests table
CREATE TABLE IF NOT EXISTS reaction_time_tests (
    test_id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    average_reaction_time FLOAT NOT NULL CHECK (average_reaction_time > 0),
    best_reaction_time FLOAT NOT NULL CHECK (best_reaction_time > 0),
    worst_reaction_time FLOAT NOT NULL CHECK (worst_reaction_time > 0),
    total_attempts INT NOT NULL CHECK (total_attempts > 0),
    successful_attempts INT NOT NULL CHECK (successful_attempts >= 0),
    accuracy_percentage FLOAT NOT NULL CHECK (accuracy_percentage >= 0 AND accuracy_percentage <= 100),
    assessment_type ENUM('baseline', 'post_injury', 'reaction_time') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_date (patient_id, assessment_date),
    INDEX idx_assessment_date (assessment_date),
    INDEX idx_reaction_time (average_reaction_time),
    INDEX idx_accuracy (accuracy_percentage)
);

-- Teams table (optional, for team management)
CREATE TABLE IF NOT EXISTS teams (
    team_id VARCHAR(50) PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    organization VARCHAR(100),
    contact_email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_team_name (team_name)
);

-- Sample data insertion
INSERT IGNORE INTO teams (team_id, team_name, organization) VALUES
('LSU_TIGERS', 'LSU Tigers', 'Louisiana State University'),
('DEMO_TEAM', 'Demo Team', 'Demo Organization');

INSERT IGNORE INTO patients (patient_id, name, team_id, age, position) VALUES
('P001', 'John Smith', 'LSU_TIGERS', 20, 'Quarterback'),
('P002', 'Mike Johnson', 'LSU_TIGERS', 21, 'Running Back'),
('P003', 'Sarah Wilson', 'LSU_TIGERS', 19, 'Defender'),
('P004', 'Tom Brown', 'DEMO_TEAM', 22, 'Forward'),
('P005', 'Lisa Davis', 'DEMO_TEAM', 20, 'Midfielder');

-- Sample symptom assessments
INSERT IGNORE INTO symptom_assessments (
    symptom_id, patient_id, assessment_date, headache_severity, nausea_severity, 
    dizziness_severity, confusion_severity, memory_problems_severity, 
    emotional_symptoms_severity, total_symptom_score, assessment_type
) VALUES
('S001', 'P001', '2024-01-15 10:00:00', 2, 1, 0, 1, 2, 1, 35, 'baseline'),
('S002', 'P001', '2024-01-20 14:30:00', 4, 3, 2, 3, 4, 3, 78, 'post_injury'),
('S003', 'P002', '2024-01-15 11:00:00', 1, 0, 1, 0, 1, 0, 15, 'baseline'),
('S004', 'P002', '2024-01-22 09:15:00', 3, 2, 1, 2, 3, 2, 55, 'post_injury'),
('S005', 'P003', '2024-01-16 15:45:00', 0, 0, 0, 0, 1, 1, 8, 'baseline'),
('S006', 'P004', '2024-01-17 13:20:00', 2, 1, 1, 1, 2, 1, 42, 'baseline'),
('S007', 'P005', '2024-01-18 16:10:00', 1, 1, 0, 0, 1, 2, 25, 'baseline');

-- Sample reaction time tests
INSERT IGNORE INTO reaction_time_tests (
    test_id, patient_id, assessment_date, average_reaction_time, best_reaction_time,
    worst_reaction_time, total_attempts, successful_attempts, accuracy_percentage, assessment_type
) VALUES
('R001', 'P001', '2024-01-15 10:30:00', 245.5, 198.2, 312.1, 50, 47, 94.0, 'baseline'),
('R002', 'P001', '2024-01-20 15:00:00', 298.7, 241.3, 387.9, 50, 42, 84.0, 'post_injury'),
('R003', 'P002', '2024-01-15 11:30:00', 234.2, 189.5, 289.7, 50, 48, 96.0, 'baseline'),
('R004', 'P002', '2024-01-22 09:45:00', 267.8, 215.4, 345.2, 50, 45, 90.0, 'post_injury'),
('R005', 'P003', '2024-01-16 16:15:00', 221.1, 178.9, 278.4, 50, 49, 98.0, 'baseline'),
('R006', 'P004', '2024-01-17 13:50:00', 258.9, 203.7, 324.5, 50, 46, 92.0, 'baseline'),
('R007', 'P005', '2024-01-18 16:40:00', 242.3, 192.1, 301.8, 50, 47, 94.0, 'baseline');
