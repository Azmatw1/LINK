from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
app=FastAPI()
class Booking(BaseModel):
    centre:str
    date:str
    time:str
    crop:str
    quantity:int
@app.post("/book")
def book_slot(booking:Booking):
    connection = sqlite3.connect("link.db")
    cursor=connection.cursor()
    cursor.execute("""
    SELECT MAX(token)
    FROM bookings
    WHERE centre=? AND date=?
    """,(booking.centre, booking.date))
    result=cursor.fetchone()
    if result[0] is None:
        token=1
    else:
        token = result[0]+1

    cursor.execute("""
    INSERT INTO bookings (centre, date, time, crop, quantity, token)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                booking.centre,
                booking.date,
                booking.time,
                booking.crop,
                booking.quantity,
                token
            ))

    connection.commit()
    connection.close()



    
    return{"message" :"Slot booked", "token":token}
    
    
@app.get("/")
def home():
    return{"message":"LINK Backend is running."}