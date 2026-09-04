from db import get_connection


def replace_priorities(student_id, priorities):
    """priorities: list of dicts with course_id and rank (1 = highest)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM priorities WHERE student_id = %s", (student_id,))
        if priorities:
            cursor.executemany(
                "INSERT INTO priorities (student_id, course_id, `rank`) VALUES (%s, %s, %s)",
                [(student_id, p["course_id"], p["rank"]) for p in priorities],
            )
        conn.commit()
    finally:
        conn.close()
    return get_priorities_for_student(student_id)


def get_priorities_for_student(student_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM priorities WHERE student_id = %s ORDER BY `rank`",
            (student_id,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_all_priorities():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM priorities")
        return cursor.fetchall()
    finally:
        conn.close()
