#flask is the web framework that will run our backend.
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sqlite3


#create flask application
app = Flask(__name__)

# Allow our frontend to communicate with Flask
CORS(app)

# DATABASE CONNECTION
def get_db():
      # Open our SQLite database
    connection = sqlite3.connect("link.db")

    # Makes database rows behave like dictionaries
    connection.row_factory = sqlite3.Row

    return connection
@app.get("/")
def home():
    return{
        "message":"LINK Backend is running."
    }

# REGISTER FARMER
@app.post("/api/register")
def register():
    # Get the data sent by the frontend
    data= request.get_json()

    # Take out the four fields we need
    full_name = data.get("fullName")
    phone_number = data.get("phoneNumber")
    village = data.get("village")
    password = data.get("password")

 # Make sure nothing is missing
    if not full_name or not phone_number or not village or not password:
        return jsonify({
            "message": "All fields are required."
        }), 400

    connection = get_db()
    cursor = connection.cursor()

    # Check whether this phone number already exists
    cursor.execute(
        "SELECT id FROM users WHERE phone_number = ?",
        (phone_number,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        connection.close()

        return jsonify({
            "message": "Phone number already registered."
        }), 409

    # Insert the new farmer
    cursor.execute("""
        INSERT INTO users
        (full_name, phone_number, village, password)
        VALUES (?, ?, ?, ?)
    """, (
        full_name,
        phone_number,
        village,
        password
    ))
    connection.commit()
    connection.close()
    return jsonify({
        "message": "Registration successful."
    }), 201

# LOGIN FARMER
@app.post("/api/login")
def login():

    # Get data sent by frontend
    data = request.get_json()

    phone_number = data.get("phoneNumber")
    password = data.get("password")

    # Check that both fields were provided
    if not phone_number or not password:
        return jsonify({
            "message": "Phone number and password are required."
        }), 400

    connection = get_db()
    cursor = connection.cursor()

    # Find the farmer with this phone number and password
    cursor.execute("""
        SELECT id, full_name
        FROM users
        WHERE phone_number = ? AND password = ?
    """, (
        phone_number,
        password
    ))

    user = cursor.fetchone()

    connection.close()

    # No matching farmer
    if user is None:
        return jsonify({
            "message": "Invalid phone number or password."
        }), 401
     # Login successful
    return jsonify({
        "message": "Login successful.",
        "userId": user["id"],
        "fullName": user["full_name"]
    }), 200

# GET PROCUREMENT CENTRES
@app.get("/api/centers")
def get_centers():
    # Connect to database
    connection = get_db()
    cursor = connection.cursor()
    # Get all procurement centres
    cursor.execute("""
        SELECT id, center_name
        FROM procurement_centers
        ORDER BY center_name
    """)

    rows = cursor.fetchall()

    connection.close()
    # Convert database rows into JSON-friendly data
    centers = []

    for row in rows:
        centers.append({
            "id": row["id"],
            "name": row["center_name"]
        })

    return jsonify(centers), 200
@app.get("/api/time-slots")
def get_time_slots():

    center_id = request.args.get("center_id")
    booking_date = request.args.get("date")

    if not center_id or not booking_date:
        return jsonify({
            "message": "Centre and date are required."
        }), 400

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            start_time,
            end_time,
            farmer_capacity,
            produce_capacity_kg
        FROM time_slots
        WHERE center_id = ?
          AND booking_date = ?
        ORDER BY start_time
    """, (center_id, booking_date))

    rows = cursor.fetchall()
    connection.close()

    slots = []

    for row in rows:
        slots.append({
            "id": row["id"],
            "startTime": row["start_time"],
            "endTime": row["end_time"],
            "farmerCapacity": row["farmer_capacity"],
            "produceCapacityKg": row["produce_capacity_kg"]
        })

    return jsonify(slots), 200

@app.post("/api/book-slot")
def book_slot():
    data = request.get_json()
    user_id = data.get("userId")
    center_id = data.get("centerId")
    slot_id = data.get("slotId")
    crop = data.get("crop")
    variety = data.get("variety")
    grade = data.get("grade")
    box_count = data.get("boxCount")
    box_weight_kg = data.get("boxWeightKg")
    total_quantity_kg = data.get("totalQuantityKg")

    # Basic required fields
    if not user_id or not center_id or not slot_id or not crop:
        return jsonify({
            "message": "Missing required booking information."
        }), 400

    connection = get_db()
    cursor = connection.cursor()

     # Check that the selected slot belongs to the selected centre
    cursor.execute("""
        SELECT
            id,
            center_id,
            booking_date,
            farmer_capacity,
            produce_capacity_kg
        FROM time_slots
        WHERE id = ?
          AND center_id = ?
    """, (slot_id, center_id))

    slot = cursor.fetchone()

    if slot is None:
        connection.close()

        return jsonify({
            "message": "Invalid time slot."
        }), 400
     # Count farmers already booked in this slot
    cursor.execute("""
        SELECT COUNT(*) AS farmer_count
        FROM bookings
        WHERE slot_id = ?
    """, (slot_id,))

    farmer_count = cursor.fetchone()["farmer_count"]

    if farmer_count >= slot["farmer_capacity"]:
        connection.close()

        return jsonify({
            "message": "This time slot is full."
        }), 409
    # Calculate already booked produce
    cursor.execute("""
        SELECT COALESCE(SUM(total_quantity_kg), 0) AS booked_quantity
        FROM bookings
        WHERE slot_id = ?
    """, (slot_id,))

    booked_quantity = cursor.fetchone()["booked_quantity"]

    # Make sure quantity is valid
    if not total_quantity_kg or float(total_quantity_kg) <= 0:
        connection.close()
        return jsonify({
            "message": "Invalid quantity."
        }), 400

    total_quantity_kg = float(total_quantity_kg)

    # Check produce capacity
    if booked_quantity + total_quantity_kg > slot["produce_capacity_kg"]:
        connection.close()

        return jsonify({
            "message": "Not enough produce capacity remaining in this slot."
        }), 409
      # Generate token number for this centre + date
    cursor.execute("""
        SELECT COALESCE(MAX(token_number), 0) + 1 AS next_token
        FROM bookings
        WHERE center_id = ?
          AND slot_id IN (
              SELECT id
              FROM time_slots
              WHERE center_id = ?
                AND booking_date = ?
          )
    """, (
        center_id,
        center_id,
        slot["booking_date"]
    ))

    token_number = cursor.fetchone()["next_token"]
     # Save booking
    booked_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO bookings (
            user_id,
            center_id,
            slot_id,
            crop,
            variety,
            grade,
            box_count,
            box_weight_kg,
            total_quantity_kg,
            token_number,
            booked_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
    """, (
        user_id,
        center_id,
        slot_id,
        crop,
        variety,
        grade,
        box_count,
        box_weight_kg,
        total_quantity_kg,
        token_number,
        booked_at
    ))
    connection.commit()
    connection.close()

    return jsonify({
    "message": "Slot booked successfully.",
    "tokenNumber": token_number,
    "bookingId": cursor.lastrowid
}), 201

@app.get("/api/queue")
def get_queue():
    center_id = request.args.get("center_id")
    booking_date = request.args.get("date")

    if not center_id or not booking_date:
        return jsonify({
            "message": "Centre and date are required."
        }), 400
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            bookings.id,
            bookings.token_number,
            bookings.crop,
            bookings.total_quantity_kg,
            bookings.booked_at,
            bookings.procurement_status,
            time_slots.start_time,
            time_slots.end_time
        FROM bookings
        JOIN time_slots
            ON bookings.slot_id = time_slots.id
        WHERE bookings.center_id = ?
          AND time_slots.booking_date = ?
          AND bookings.procurement_status = 'Waiting'
        ORDER BY
            time_slots.start_time ASC,
            bookings.booked_at ASC,
            bookings.token_number ASC
    """, (center_id, booking_date))
    rows = cursor.fetchall()
    connection.close()

    queue = []

    for row in rows:
        queue.append({
            "bookingId": row["id"],
            "tokenNumber": row["token_number"],
            "crop": row["crop"],
            "quantityKg": row["total_quantity_kg"],
            "bookedAt": row["booked_at"],
            "slotStart": row["start_time"],
            "slotEnd": row["end_time"],
            "status": row["procurement_status"]
        })

    return jsonify(queue), 200

@app.get("/api/my-bookings")
def get_my_bookings():

    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({
            "message": "User ID is required."
        }), 400

    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            bookings.id,
            bookings.token_number,
            bookings.crop,
            bookings.total_quantity_kg,
            bookings.procurement_status,
            bookings.payment_status,
            procurement_centers.id AS center_id,
            procurement_centers.center_name,
            time_slots.booking_date,
            time_slots.start_time,
            time_slots.end_time
        FROM bookings
        JOIN procurement_centers
            ON bookings.center_id = procurement_centers.id
        JOIN time_slots
            ON bookings.slot_id = time_slots.id
        WHERE bookings.user_id = ?
        ORDER BY
            time_slots.booking_date DESC,
            bookings.booked_at DESC
    """, (user_id,))

    rows = cursor.fetchall()
    connection.close()
    bookings = []

    for row in rows:
        bookings.append({
            "bookingId": row["id"],
            "tokenNumber": row["token_number"],
            "crop": row["crop"],
            "totalQuantityKg": row["total_quantity_kg"],
            "status": row["procurement_status"],
            "paymentStatus": row["payment_status"],
            "centerId": row["center_id"],
            "centerName": row["center_name"],
            "bookingDate": row["booking_date"],
            "slotStart": row["start_time"],
            "slotEnd": row["end_time"]
        })

    return jsonify(bookings), 200





    



if __name__=="__main__":
     app.run(debug=True)


