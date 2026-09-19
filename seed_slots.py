import sqlite3

connection = sqlite3.connect("link.db")
cursor = connection.cursor()

# Get all procurement centres
cursor.execute("""
    SELECT id, center_name
    FROM procurement_centers
""")

centres = cursor.fetchall()
# Demo slots for each centre
slots = [
    ("09:00", "10:00"),
    ("10:00", "11:00"),
    ("11:00", "12:00"),
    ("12:00", "13:00"),
    ("14:00", "15:00"),
    ("15:00", "16:00"),
    ("16:00", "17:00")
]

# Demo capacities
farmer_capacity = 20
produce_capacity = 500
# Use today's date for our first demo slots
from datetime import date
booking_date = date.today().isoformat()

for centre_id, centre_name in centres:

    for start_time, end_time in slots:

        cursor.execute("""
            SELECT id
            FROM time_slots
            WHERE center_id = ?
              AND booking_date = ?
              AND start_time = ?
              AND end_time = ?
        """, (
            centre_id,
            booking_date,
            start_time,
            end_time
        ))

        existing = cursor.fetchone()

        if existing is None:

            cursor.execute("""
 INSERT INTO time_slots
                (
                    center_id,
                    booking_date,
                    start_time,
                    end_time,
                    farmer_capacity,
                    produce_capacity_kg
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                centre_id,
                booking_date,
                start_time,
                end_time,
                farmer_capacity,
                produce_capacity
            ))

connection.commit()

print("\nLINK Time Slots:")
cursor.execute("""
    SELECT
        time_slots.id,
        procurement_centers.center_name,
        time_slots.booking_date,
        time_slots.start_time,
        time_slots.end_time,
        time_slots.farmer_capacity,
        time_slots.produce_capacity_kg
    FROM time_slots
    JOIN procurement_centers
        ON time_slots.center_id = procurement_centers.id
    ORDER BY procurement_centers.center_name, time_slots.start_time
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

connection.close()