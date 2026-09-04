from db import get_connection


def clear_schedule():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM schedule")
        conn.commit()
    finally:
        conn.close()


def create_schedule_entry(course_id, room_id, time_slot):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO schedule (course_id, room_id, time_slot) VALUES (%s, %s, %s)",
            (course_id, room_id, time_slot),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_schedule_by_id(schedule_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM schedule WHERE id = %s", (schedule_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_schedule_for_course(course_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM schedule WHERE course_id = %s", (course_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_all_schedule():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM schedule")
        return cursor.fetchall()
    finally:
        conn.close()
