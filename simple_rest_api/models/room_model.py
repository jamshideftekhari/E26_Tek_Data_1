from db import get_connection


def create_room(name, capacity, time_slot):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO rooms (name, capacity, time_slot) VALUES (%s, %s, %s)",
            (name, capacity, time_slot),
        )
        conn.commit()
        new_id = cursor.lastrowid
    finally:
        conn.close()
    return get_room(new_id)


def get_room(room_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rooms WHERE id = %s", (room_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_all_rooms():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rooms ORDER BY id")
        return cursor.fetchall()
    finally:
        conn.close()
