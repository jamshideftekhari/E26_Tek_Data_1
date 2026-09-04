from db import get_connection


def create_student(name, email):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, email) VALUES (%s, %s)", (name, email)
        )
        conn.commit()
        new_id = cursor.lastrowid
    finally:
        conn.close()
    return get_student(new_id)


def get_student(student_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_all_students():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students")
        return cursor.fetchall()
    finally:
        conn.close()
