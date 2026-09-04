from db import get_connection


def clear_allocations():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM allocations")
        conn.commit()
    finally:
        conn.close()


def create_allocation(schedule_id, student_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO allocations (schedule_id, student_id) VALUES (%s, %s)",
            (schedule_id, student_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_allocations_for_schedule(schedule_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM allocations WHERE schedule_id = %s", (schedule_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_allocation_for_student(student_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM allocations WHERE student_id = %s LIMIT 1", (student_id,)
        )
        return cursor.fetchone()
    finally:
        conn.close()
