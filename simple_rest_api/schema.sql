CREATE DATABASE IF NOT EXISTS elective_registration;
USE elective_registration;

CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_name VARCHAR(120) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    capacity INT NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS priorities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    `rank` INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    capacity INT NOT NULL,
    time_slot VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    room_id INT NOT NULL,
    time_slot VARCHAR(50) NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

CREATE TABLE IF NOT EXISTS allocations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL,
    student_id INT NOT NULL,
    FOREIGN KEY (schedule_id) REFERENCES schedule(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);
