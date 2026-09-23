from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)
# Database connection
def get_db():
    # Connect to the same database used by the farmer backend.
    connection = sqlite3.connect("link.db")

    # Allows us to access columns by their names.
    connection.row_factory = sqlite3.Row

    return connection

# Get today's centre bookings
@app.get("/api/center-bookings")
def get_center_bookings():

    # Get centre ID and date from the request.
    center_id = request.args.get("center_id")
    booking_date = request.args.get("date")

    # Make sure both values were provided.
    if not center_id or not booking_date:
        return jsonify({
            "message": "Centre ID and date are required."
        }), 400

    connection = get_db()
    cursor = connection.cursor()

    # Get bookings for this centre and date.
    cursor.execute("""
        SELECT
            bookings.id,
            bookings.token_number,
            bookings.crop,
            bookings.total_quantity_kg,
            bookings.procurement_status,
            bookings.payment_status,
            time_slots.start_time,
            time_slots.end_time
        FROM bookings
        JOIN time_slots
            ON bookings.slot_id = time_slots.id
        WHERE bookings.center_id = ?
          AND time_slots.booking_date = ?
        ORDER BY
            time_slots.start_time ASC,
            bookings.booked_at ASC,
            bookings.token_number ASC
    """, (center_id, booking_date))

    rows = cursor.fetchall()
    connection.close()
    bookings = []

    # Convert database rows into JSON.
    for row in rows:

        bookings.append({
            "bookingId": row["id"],
            "tokenNumber": row["token_number"],
            "crop": row["crop"],
            "totalQuantityKg": row["total_quantity_kg"],
            "status": row["procurement_status"],
            "paymentStatus": row["payment_status"],
            "slotStart": row["start_time"],
            "slotEnd": row["end_time"]
        })

    return jsonify(bookings), 200
# Update booking status
@app.post("/api/update-status")
def update_status():

    # Read the data sent by the admin frontend.
    data = request.get_json()

    booking_id = data.get("bookingId")
    procurement_status = data.get("procurementStatus")
    payment_status = data.get("paymentStatus")

    # A booking ID is always required.
    if not booking_id:
        return jsonify({
            "message": "Booking ID is required."
        }), 400

    connection = get_db()
    cursor = connection.cursor()

    # --------------------------------
    # Update procurement status only
    # --------------------------------
    if procurement_status:

        if procurement_status not in ["Waiting", "Completed"]:
            connection.close()

            return jsonify({
                "message": "Invalid procurement status."
            }), 400

        cursor.execute("""
            UPDATE bookings
            SET procurement_status = ?
            WHERE id = ?
        """, (
            procurement_status,
            booking_id
        ))

    # --------------------------------
    # Update payment status only
    # --------------------------------
    if payment_status:

        if payment_status not in ["Pending", "Paid"]:
            connection.close()

            return jsonify({
                "message": "Invalid payment status."
            }), 400

        cursor.execute("""
            UPDATE bookings
            SET payment_status = ?
            WHERE id = ?
        """, (
            payment_status,
            booking_id
        ))

    # Make sure the booking actually exists.
    if cursor.rowcount == 0:

        # The rowcount can be 0 if the same value
        # was already stored, so check the booking directly.
        cursor.execute("""
            SELECT id
            FROM bookings
            WHERE id = ?
        """, (booking_id,))

        if not cursor.fetchone():
            connection.close()

            return jsonify({
                "message": "Booking not found."
            }), 404

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Booking status updated successfully."
    }), 200

  



# Start admin backend


if __name__ == "__main__":

    # Use port 5001 because farmer main.py uses port 5000.
    app.run(debug=True, port=5001)