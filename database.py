import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "farmer_app.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone_number TEXT UNIQUE NOT NULL,
        state TEXT NOT NULL,
        village TEXT NOT NULL,
        password TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number TEXT NOT NULL,
        center TEXT NOT NULL,
        crop TEXT NOT NULL,
        quantity REAL NOT NULL,
        booking_date TEXT NOT NULL,
        time_slot TEXT NOT NULL,
        token_number TEXT UNIQUE NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS procurement_centers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        center_name TEXT NOT NULL,
        total_capacity INTEGER NOT NULL
    );
    """)

    cursor.execute("SELECT COUNT(*) FROM procurement_centers;")
    center_count = cursor.fetchone()[0]

    if center_count == 0:
        default_centers = [
            ("Mandi Center A (Main Market)", 1000),
            ("Mandi Center B (North Hub)", 800),
            ("Cooperative Grain Hub C", 1200)
        ]
        cursor.executemany(
            "INSERT INTO procurement_centers (center_name, total_capacity) VALUES (?, ?);",
            default_centers
        )

    conn.commit()
    conn.close()
    print("Database initialized successfully at:", DB_PATH)


def register_user(full_name, phone, state, village, password):
    full_name = str(full_name).strip() if full_name is not None else ""
    phone = str(phone).strip() if phone is not None else ""
    state = str(state).strip() if state is not None else ""
    village = str(village).strip() if village is not None else ""
    password = str(password).strip() if password is not None else ""

    if not all([full_name, phone, state, village, password]):
        return {"success": False, "message": "All fields are required."}

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE phone_number = ?;", (phone,))
        existing_user = cursor.fetchone()
        if existing_user:
            return {"success": False, "message": "Phone number is already registered. Please log in."}

        cursor.execute("""
            INSERT INTO users (full_name, phone_number, state, village, password)
            VALUES (?, ?, ?, ?, ?);
        """, (full_name, phone, state, village, password))

        conn.commit()
        user_id = cursor.lastrowid
        return {
            "success": True,
            "message": "User registered successfully!",
            "user_id": user_id
        }
    except Exception as error:
        return {"success": False, "message": f"Database error: {str(error)}"}
    finally:
        conn.close()


def verify_user(phone, password):
    phone = str(phone).strip() if phone is not None else ""
    password = str(password).strip() if password is not None else ""

    if not phone or not password:
        return {"success": False, "message": "Phone number and password are required."}

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, full_name, phone_number, state, village
            FROM users
            WHERE phone_number = ? AND password = ?;
        """, (phone, password))

        row = cursor.fetchone()
        if row:
            return {
                "success": True,
                "message": "Login successful!",
                "user": {
                    "id": row[0],
                    "full_name": row[1],
                    "phone_number": row[2],
                    "state": row[3],
                    "village": row[4]
                }
            }
        else:
            return {"success": False, "message": "Invalid phone number or password."}
    except Exception as error:
        return {"success": False, "message": f"Database error: {str(error)}"}
    finally:
        conn.close()


def create_slot_booking(phone, center, crop, quantity, booking_date, time_slot):
    phone = str(phone).strip() if phone is not None else ""
    center = str(center).strip() if center is not None else ""
    crop = str(crop).strip() if crop is not None else ""
    booking_date = str(booking_date).strip() if booking_date is not None else ""
    time_slot = str(time_slot).strip() if time_slot is not None else ""

    if not all([phone, center, crop, booking_date, time_slot]):
        return {"success": False, "message": "All booking details are required."}

    try:
        quantity_num = float(quantity)
        if quantity_num <= 0:
            return {"success": False, "message": "Quantity must be greater than 0."}
    except (ValueError, TypeError):
        return {"success": False, "message": "Invalid quantity format."}

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT MAX(id) FROM slots;")
        max_id_row = cursor.fetchone()
        next_sequence = 1 if (max_id_row is None or max_id_row[0] is None) else max_id_row[0] + 1
        token_number = f"#{next_sequence:03d}"

        cursor.execute("""
            INSERT INTO slots (phone_number, center, crop, quantity, booking_date, time_slot, token_number)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (phone, center, crop, quantity_num, booking_date, time_slot, token_number))

        conn.commit()
        booking_id = cursor.lastrowid

        return {
            "success": True,
            "message": "Procurement slot booked successfully!",
            "token_number": token_number,
            "booking": {
                "id": booking_id,
                "phone_number": phone,
                "center": center,
                "crop": crop,
                "quantity": quantity_num,
                "booking_date": booking_date,
                "time_slot": time_slot,
                "token_number": token_number
            }
        }
    except Exception as error:
        return {"success": False, "message": f"Database error: {str(error)}"}
    finally:
        conn.close()


def get_user_booking(phone):
    phone = str(phone).strip() if phone is not None else ""
    if not phone:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, phone_number, center, crop, quantity, booking_date, time_slot, token_number
            FROM slots
            WHERE phone_number = ?
            ORDER BY id DESC
            LIMIT 1;
        """, (phone,))

        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "phone_number": row[1],
                "center": row[2],
                "crop": row[3],
                "quantity": row[4],
                "booking_date": row[5],
                "time_slot": row[6],
                "token_number": row[7]
            }
        return None
    except Exception:
        return None
    finally:
        conn.close()


def get_all_centers():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, center_name, total_capacity FROM procurement_centers;")
        rows = cursor.fetchall()
        return [
            {"id": row[0], "center_name": row[1], "total_capacity": row[2]}
            for row in rows
        ]
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("Default Procurement Centers:")
    for center in get_all_centers():
        print(f" - {center['center_name']} (Capacity: {center['total_capacity']} quintals)")
