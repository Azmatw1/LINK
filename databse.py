import sqlite3

connection=sqlite3.connect("link.db")
cursor=connection.cursor()

#1.farmers 
# This table stores information about farmers/users.
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone_number TEXT UNIQUE NOT NULL,
    village TEXT NOT NULL,
    password TEXT NOT NULL)
""")


# 2. PROCUREMENT CENTRES TABLE
# This table stores information about procurement centres.
cursor.execute("""
CREATE TABLE IF NOT EXISTS procurement_centers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_name TEXT NOT NULL,
    -- Maximum number of farmers the centre can handle for the defined capacity period.
    farmer_capacity INTEGER NOT NULL,
    -- Maximum amount of produce the centre can handle, measured in kilograms.
    produce_capacity_kg REAL NOT NULL
)
""")

#3. TIME SLOTS TABLE
# This table stores the appointment slots available at each procurement centre.
cursor.execute("""
CREATE TABLE IF NOT EXISTS time_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_id INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    farmer_capacity INTEGER NOT NULL,
    produce_capacity_kg REAL NOT NULL,

    -- Connect this slot to the procurement centre.
    FOREIGN KEY (center_id) REFERENCES procurement_centers(id)
)
""")

# 4. BOOKINGS TABLE
# This is the MAIN table.
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    -- internal database ID.
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    center_id INTEGER NOT NULL,
    slot_id INTEGER NOT NULL,
    crop TEXT NOT NULL,
    variety TEXT,
    grade TEXT,
    box_count INTEGER,
    box_weight_kg REAL,
    total_quantity_kg REAL NOT NULL,
    token_number INTEGER NOT NULL,
    booked_at TEXT NOT NULL,
    procurement_status TEXT DEFAULT 'Waiting',
    payment_status TEXT DEFAULT 'Pending',

    --  Connect booking to farmer.
    FOREIGN KEY (user_id) REFERENCES users(id),

    -- Connect booking to procurement centre.
    FOREIGN KEY (center_id) REFERENCES procurement_centers(id),

    -- Connect booking to time slot.
    FOREIGN KEY (slot_id) REFERENCES time_slots(id)
)
""")
connection.commit()
connection.close()
print("Database setup complete!")


