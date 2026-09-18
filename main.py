"""
main.py - Lightweight Flask Web Application & REST API
======================================================
This file serves the frontend files and provides REST API endpoints for the LINK portal.

COLLEGE PRESENTATION KEY CONCEPTS:
----------------------------------
1. Flask(__name__, static_folder=BASE_DIR, static_url_path=""):
   - Initializes a new Flask web application instance.
   - Pointing static_folder to the current directory allows Flask to directly serve
     index.html, styles (looks.css), and scripts (script.js) to the web browser.

2. CORS(app):
   - Enables "Cross-Origin Resource Sharing".
   - Browsers block web requests made across different ports or domains by default.
     CORS sets HTTP headers that permit our frontend JavaScript (fetch) to safely communicate
     with backend API routes.

3. request.get_json():
   - In Flask, when a frontend sends data via POST using fetch() with 'Content-Type: application/json',
     request.get_json() parses the raw HTTP body and converts it into a Python dictionary.
   - If the request body is not valid JSON or missing, it safely returns None.

4. jsonify(data):
   - Serializes a Python dictionary or list into an HTTP JSON response string.
   - It automatically attaches the HTTP header 'Content-Type: application/json' and returns
     the appropriate HTTP status code (e.g., 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized).

5. send_from_directory(directory, filename):
   - Securely serves static files (HTML, CSS, JS, images) from a given directory to the client browser
     while preventing directory traversal attacks.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import database

# Current project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize the lightweight Flask application
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")

# Enable CORS for all routes so frontend fetch() calls never get blocked
CORS(app)

# Ensure the database tables and default procurement centers exist on server startup
database.init_db()


# ==============================================================================
# STATIC FRONTEND ROUTES
# ==============================================================================

@app.route("/")
def serve_index():
    """
    Route: GET /
    Serves the default landing page (index.html - Farmer Login)
    when visiting http://127.0.0.1:5000 in a browser.
    """
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    """
    Route: GET /<filename>
    Serves static HTML pages (register.html, booking.html, token.html, dashboard.html),
    stylesheets (looks.css), and JavaScript files (script.js).
    """
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(BASE_DIR, filename)
    return jsonify({"success": False, "message": "Resource not found"}), 404


# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@app.route("/api/register", methods=["POST"])
def api_register():
    """
    Endpoint: POST /api/register
    Purpose: Registers a new farmer account.
    
    Expected JSON Input:
    {
        "fullName": "Ramesh Kumar",
        "phoneNumber": "9876543210",
        "state": "Punjab",
        "village": "Rampur",
        "password": "secretpassword"
    }
    
    College Presentation Explanation:
    - `request.get_json()` extracts the JSON payload sent by fetch() from JavaScript.
    - Input values are extracted and validated to ensure no field is left blank.
    - We call `database.register_user(...)` to persist the record using SQLite.
    - `jsonify()` converts our Python result dictionary into a JSON response with status code 201 or 400.
    """
    # 1. Parse JSON payload from incoming HTTP POST request
    data = request.get_json() or {}

    # 2. Extract values (supporting both camelCase and snake_case from frontend)
    full_name = data.get("fullName") or data.get("full_name")
    phone = data.get("phoneNumber") or data.get("phone_number") or data.get("phone")
    state = data.get("state")
    village = data.get("village")
    password = data.get("password")

    # 3. Input validation
    if not all([full_name, phone, state, village, password]):
        return jsonify({
            "success": False,
            "message": "All fields (Full Name, Phone, State, Village, Password) are required."
        }), 400

    # 4. Invoke database helper function to create user
    result = database.register_user(full_name, phone, state, village, password)

    # 5. Return appropriate JSON response and HTTP status code
    if result.get("success"):
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route("/api/login", methods=["POST"])
def api_login():
    """
    Endpoint: POST /api/login
    Purpose: Verifies farmer credentials (phone & password).
    
    Expected JSON Input:
    {
        "phoneNumber": "9876543210",
        "password": "secretpassword"
    }
    
    College Presentation Explanation:
    - `request.get_json()` retrieves the user's login credentials.
    - `database.verify_user()` queries the SQLite 'users' table using SQL parameter binding.
    - If valid, returns HTTP 200 with user profile info; if invalid, returns HTTP 401 Unauthorized.
    """
    # 1. Parse JSON payload
    data = request.get_json() or {}

    # 2. Extract phone and password
    phone = data.get("phoneNumber") or data.get("phone_number") or data.get("phone")
    password = data.get("password")

    # 3. Basic validation
    if not phone or not password:
        return jsonify({
            "success": False,
            "message": "Phone number and password are required."
        }), 400

    # 4. Verify credentials in database
    result = database.verify_user(phone, password)

    # 5. Return HTTP 200 on success, or HTTP 401 on invalid credentials
    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify(result), 401


@app.route("/api/book-slot", methods=["POST"])
def api_book_slot():
    """
    Endpoint: POST /api/book-slot
    Purpose: Books a procurement time slot and assigns a unique sequential token (e.g., #001).
    
    Expected JSON Input:
    {
        "phoneNumber": "9876543210",
        "center": "Mandi Center A (Main Market)",
        "crop": "wheat",
        "quantity": 50,
        "bookingDate": "2026-10-15",
        "timeSlot": "09:00-11:00"
    }
    
    College Presentation Explanation:
    - `request.get_json()` reads the appointment scheduling parameters.
    - `database.create_slot_booking()` calculates the next sequential token number (#001, #002...)
      and inserts the record into the 'slots' table.
    - `jsonify()` returns the assigned token to the frontend so it can be displayed on token.html.
    """
    # 1. Parse JSON payload
    data = request.get_json() or {}

    # 2. Extract booking data
    phone = data.get("userPhone") or data.get("phoneNumber") or data.get("phone_number") or data.get("phone")
    center = data.get("center") or data.get("centre")
    crop = data.get("crop")
    quantity = data.get("quantity")
    booking_date = data.get("bookingDate") or data.get("booking_date") or data.get("date")
    time_slot = data.get("timeSlot") or data.get("time_slot") or data.get("time")

    # 3. Validate presence of all booking attributes
    if not all([phone, center, crop, quantity, booking_date, time_slot]):
        return jsonify({
            "success": False,
            "message": "Please provide all booking details (Phone, Center, Crop, Quantity, Date, Time Slot)."
        }), 400

    # 4. Save booking and generate sequential token
    result = database.create_slot_booking(phone, center, crop, quantity, booking_date, time_slot)

    # 5. Return HTTP 201 on success or 400 on error
    if result.get("success"):
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route("/api/my-token", methods=["GET"])
@app.route("/api/user-booking", methods=["GET"])
def api_my_token():
    """
    Endpoint: GET /api/my-token?phone=9876543210
    Purpose: Reads userPhone and returns their actual assigned token and booking details.
    
    If booking exists: returns { "success": True, "token_number": ..., "booking": ... }
    If NO booking exists: returns { "success": False, "message": "No active slot booked yet" }, 404
    """
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
    """
    Endpoint: GET /api/centers
    Purpose: Returns the list of government procurement centers.
    """
    centers = database.get_all_centers()
    return jsonify({"success": True, "centers": centers}), 200


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    # Runs the local development server at http://127.0.0.1:5000
    # debug=True enables auto-reloading when code changes and detailed browser error pages
    print("=====================================================")
    print(" LINK Backend Server Running!")
    print(" Open in Browser: http://127.0.0.1:5000")
    print("=====================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)