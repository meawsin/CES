-- Update database structure to allow NULL course_code for batch/session-only evaluations
USE CourseEvaluationSystem;

-- Update evaluations table to allow NULL course_code
ALTER TABLE evaluations MODIFY COLUMN course_code VARCHAR(20) DEFAULT NULL;

-- Update evaluation_completion table to allow NULL course_code
ALTER TABLE evaluation_completion MODIFY COLUMN course_code VARCHAR(20) DEFAULT NULL;

-- Update any existing "N/A" values to NULL in both tables
UPDATE evaluations SET course_code = NULL WHERE course_code = 'N/A';
UPDATE evaluation_completion SET course_code = NULL WHERE course_code = 'N/A';

-- Verify the changes
DESCRIBE evaluations;
DESCRIBE evaluation_completion; 