import sqlite3

# Connect to our existing LINK database
connection = sqlite3.connect("link.db")
cursor = connection.cursor()
# Our demo procurement / collection centres
centres = [
    "Fruit Mandi Parimpora",
    "Fruit Mandi Sopore",
    "Arhama / Shopian Collection Point",
    "Jablipora",
    "Botengoo"
]
# Add each centre only if it doesn't already exist
for centre in centres:

    cursor.execute("""
        SELECT id
        FROM procurement_centers
        WHERE center_name = ?
    """, (centre,))

    existing = cursor.fetchone()

    if existing is None:

        cursor.execute("""
            INSERT INTO procurement_centers
            (center_name, farmer_capacity, produce_capacity_kg)
            VALUES (?, ?, ?)
        """, (
            centre,
            100,       # demo farmer capacity
            5000       # demo produce capacity in kg
        ))

# Save changes
connection.commit()
# Check what we have
cursor.execute("""
    SELECT id, center_name
    FROM procurement_centers
""")

centres = cursor.fetchall()

print("\nLINK Procurement Centres:")
for centre in centres:
    print(centre)

connection.close()