from db import get_connection


def create_course(teacher_name, code, title, description, capacity):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO courses (teacher_name, code, title, description, capacity)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (teacher_name, code, title, description, capacity),
        )
        conn.commit()
        new_id = cursor.lastrowid
    finally:
        conn.close()
    return get_course(new_id)


def get_course(course_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_all_courses():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM courses")
        return cursor.fetchall()
    finally:
        conn.close()
