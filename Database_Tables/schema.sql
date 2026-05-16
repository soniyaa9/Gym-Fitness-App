-- ============================================================
-- Gym & Fitness Management System
-- Final SQL Schema — 3rd Normal Form Compliant
-- ============================================================

DROP SCHEMA IF EXISTS gym_db;
CREATE SCHEMA gym_db;
USE gym_db;

-- ============================================================
-- Table: trainers
-- Metadata: created_at
-- ============================================================
CREATE TABLE trainers (
    trainer_id   INT          NOT NULL AUTO_INCREMENT,
    first_name   VARCHAR(50)  NOT NULL,
    last_name    VARCHAR(50)  NOT NULL,
    email        VARCHAR(100) NOT NULL,
    phone        VARCHAR(20),
    speciality   VARCHAR(100),
    hourly_rate  DECIMAL(6,2) NOT NULL,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (trainer_id)
);

-- ============================================================
-- Table: members
-- 3NF Change: membership_duration_days removed (derived column)
-- Metadata: created_at
-- ============================================================
CREATE TABLE members (
    member_id             INT          NOT NULL AUTO_INCREMENT,
    first_name            VARCHAR(50)  NOT NULL,
    last_name             VARCHAR(50)  NOT NULL,
    email                 VARCHAR(100) NOT NULL,
    phone                 VARCHAR(20),
    date_of_birth         DATE         NOT NULL,
    membership_type       ENUM('basic','standard','premium') NOT NULL DEFAULT 'basic',
    membership_start_date DATE         NOT NULL,
    membership_end_date   DATE         NOT NULL,
    trainer_id            INT,
    created_at            DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (member_id),
    CONSTRAINT uq_members_email    UNIQUE (email),
    CONSTRAINT fk_members_trainer  FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id)
);

-- ============================================================
-- Table: equipment
-- Metadata: last_updated (auto-updates on every change)
-- ============================================================
CREATE TABLE equipment (
    equipment_id     INT          NOT NULL AUTO_INCREMENT,
    equipment_name   VARCHAR(100) NOT NULL,
    category         VARCHAR(60)  NOT NULL,
    quantity         INT          NOT NULL DEFAULT 1,
    condition_status ENUM('excellent','good','fair','needs_repair') NOT NULL DEFAULT 'good',
    purchase_date    DATE         NOT NULL,
    last_updated     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (equipment_id)
);

-- ============================================================
-- Table: classes
-- Metadata: created_at
-- ============================================================
CREATE TABLE classes (
    class_id      INT          NOT NULL AUTO_INCREMENT,
    class_name    VARCHAR(100) NOT NULL,
    trainer_id    INT          NOT NULL,
    class_date    DATE         NOT NULL,
    start_time    TIME         NOT NULL,
    duration_mins INT          NOT NULL,
    max_capacity  INT          NOT NULL DEFAULT 20,
    room          VARCHAR(50),
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (class_id),
    CONSTRAINT fk_classes_trainer FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id)
);

-- ============================================================
-- Table: class_enrollments
-- Metadata: enrolled_at
-- ============================================================
CREATE TABLE class_enrollments (
    enrollment_id INT      NOT NULL AUTO_INCREMENT,
    member_id     INT      NOT NULL,
    class_id      INT      NOT NULL,
    attendance    ENUM('registered','attended','no_show') NOT NULL DEFAULT 'registered',
    enrolled_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (enrollment_id),
    CONSTRAINT fk_enroll_member FOREIGN KEY (member_id) REFERENCES members(member_id),
    CONSTRAINT fk_enroll_class  FOREIGN KEY (class_id)  REFERENCES classes(class_id)
);

-- ============================================================
-- Sample Data
-- ============================================================
INSERT INTO trainers (first_name, last_name, email, phone, speciality, hourly_rate) VALUES
    ('Soniya',  'Shah',     'soniya.shah@gymfit.com',    '316-555-0201', 'Weightlifting', 45.00),
    ('Sofia',   'Patel',    'sofia.patel@gymfit.com',    '316-555-0202', 'Yoga',          40.00),
    ('Shivam',  'Shah',     'shivam.shah@gymfit.com',    '316-555-0203', 'Cardio & HIIT', 42.00),
    ('Aisha',   'Thompson', 'aisha.thompson@gymfit.com', '316-555-0204', 'Pilates',       38.00),
    ('Derek',   'Nguyen',   'derek.nguyen@gymfit.com',   '316-555-0205', 'Nutrition',     50.00),
    ('Lena',    'Morales',  'lena.morales@gymfit.com',   '316-555-0206', 'CrossFit',      46.00);

INSERT INTO members (first_name, last_name, email, phone, date_of_birth, membership_type, membership_start_date, membership_end_date, trainer_id) VALUES
    ('Himanshu', 'Shah',    'himan@email.com',  '315-555-6666', '2002-02-08', 'premium',  '2025-01-17', '2026-01-01', 1),
    ('Hema',     'Doe',     'hema@email.com',   '315-555-0202', '2002-03-08', 'standard', '2025-01-03', '2026-09-11', 2),
    ('Hari',     'Singh',   'hari@email.com',   '315-555-7374', '1998-02-19', 'basic',    '2025-03-01', '2026-01-01', NULL),
    ('Rekha',    'Evans',   'rekha@email.com',  '315-555-6774', '2012-08-07', 'premium',  '2025-06-04', '2026-05-01', 3),
    ('Smith',    'Johnson', 'smith@email.com',  '315-555-7387', '1989-02-18', 'standard', '2025-08-01', '2026-01-29', 4),
    ('Tenor',    'White',   'tenor@email.com',  '315-555-6847', '1988-05-25', 'basic',    '2025-05-01', '2026-12-01', NULL);

INSERT INTO equipment (equipment_name, category, quantity, condition_status, purchase_date) VALUES
    ('Treadmill',        'Cardio',      10, 'good',         '2014-03-05'),
    ('Yoga Mat',         'Flexibility', 15, 'excellent',    '2023-01-10'),
    ('Stationary Bike',  'Cardio',       8, 'good',         '2022-04-08'),
    ('Cable Machine',    'Strength',     6, 'fair',         '2020-10-10'),
    ('Rowing Machine',   'Cardio',       4, 'excellent',    '2019-06-05'),
    ('Barbell',          'Strength',    30, 'good',         '2024-05-05');

INSERT INTO classes (class_name, trainer_id, class_date, start_time, duration_mins, max_capacity, room) VALUES
    ('Morning Yoga',        2, '2026-04-10', '07:00:00', 60, 15, 'Studio A'),
    ('HIIT Blast',          3, '2026-04-09', '09:00:00', 45, 20, 'Main Floor'),
    ('Pilates Core',        4, '2026-04-10', '10:00:00', 50, 12, 'Studio B'),
    ('Powerlifting 101',    1, '2026-04-10', '06:00:00', 60, 18, 'Weight Room'),
    ('CrossFit Challenge',  6, '2026-04-09', '18:30:00', 45, 20, 'Main Floor'),
    ('Evening Spin',        3, '2026-04-02', '17:00:00', 45, 20, 'Spin Room');

INSERT INTO class_enrollments (member_id, class_id, attendance) VALUES
    (1, 1, 'attended'),
    (2, 1, 'attended'),
    (4, 3, 'registered'),
    (5, 4, 'attended'),
    (6, 5, 'registered'),
    (1, 6, 'registered'),
    (2, 4, 'attended');
