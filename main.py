import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")

CORS(app)

database.init_db()


@app.route("/")
def serve_index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(BASE_DIR, filename)
    return jsonify({"success": False, "message": "Resource not found"}), 404


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}

    full_name = data.get("fullName") or data.get("full_name")
    phone = data.get("phoneNumber") or data.get("phone_number") or data.get("phone")
    state = data.get("state")
    village = data.get("village")
    password = data.get("password")

    if not all([full_name, phone, state, village, password]):
        return jsonify({
            "success": False,
            "message": "All fields (Full Name, Phone, State, Village, Password) are required."
        }), 400

    result = database.register_user(full_name, phone, state, village, password)

    if result.get("success"):
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}

    phone = data.get("phoneNumber") or data.get("phone_number") or data.get("phone")
    password = data.get("password")

    if not phone or not password:
        return jsonify({
            "success": False,
            "message": "Phone number and password are required."
        }), 400

    result = database.verify_user(phone, password)

    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify(result), 401


@app.route("/api/book-slot", methods=["POST"])
def api_book_slot():
    data = request.get_json() or {}

    phone = data.get("userPhone") or data.get("phoneNumber") or data.get("phone_number") or data.get("phone")
    center = data.get("center") or data.get("centre")
    crop = data.get("crop")
    quantity = data.get("quantity")
    booking_date = data.get("bookingDate") or data.get("booking_date") or data.get("date")
    time_slot = data.get("timeSlot") or data.get("time_slot") or data.get("time")

    if not all([phone, center, crop, quantity, booking_date, time_slot]):
        return jsonify({
            "success": False,
            "message": "Please provide all booking details (Phone, Center, Crop, Quantity, Date, Time Slot)."
        }), 400

    result = database.create_slot_booking(phone, center, crop, quantity, booking_date, time_slot)

    if result.get("success"):
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route("/api/my-token", methods=["GET"])
@app.route("/api/user-booking", methods=["GET"])
def api_my_token():
    phone = request.args.get("phone")
    if not phone:
        return jsonify({"success": False, "message": "Query parameter 'phone' is required."}), 400

    booking = database.get_user_booking(phone)
    if booking:
        return jsonify({
            "success": True,
            "token_number": booking.get("token_number"),
            "booking": booking
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "No active slot booked yet"
        }), 404


@app.route("/api/centers", methods=["GET"])
def api_get_centers():
    centers = database.get_all_centers()
    return jsonify({"success": True, "centers": centers}), 200


if __name__ == "__main__":
    print("=====================================================")
    print(" LINK Backend Server Running!")
    print(" Open in Browser: http://127.0.0.1:5000")
    print("=====================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)
