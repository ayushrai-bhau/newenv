from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from pymongo import MongoClient
from datetime import datetime

from bson import ObjectId
from routes import book_routes,member_routes,borrowing_routes
from models.borrowing import Borrowing 
from db.mongodb import borrowings_collection

from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv()


# MongoDB Atlas connection string
MONGO_URI = os.getenv("DB_URL")

# Create a MongoClient instance
client = MongoClient(MONGO_URI)

# Get the database
db = client.get_database("LMS")

# Get the books collection
books_collection = db.books
members_collection = db.members

# Create a FastAPI instance
app = FastAPI()

app.include_router(book_routes.router)
app.include_router(member_routes.router)
app.include_router(borrowing_routes.router)


@app.post("/return/{book_id}/{member_id}")
async def return_book(book_id: str, member_id: str):
    # Fetch the book from the database
    book =  db.books.find_one({"id": book_id})
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    # Fetch the member from the database
    member =  db.members.find_one({"id": member_id})
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    if book["borrowed"] is False:
        raise HTTPException(status_code=400, detail="Book is not borrowed")

    if book_id not in member["borrowed_books"]:
        raise HTTPException(status_code=400, detail="Book is not borrowed by the member")

    # Update the book's borrowed status in the database
    db.books.update_one({"id": book_id}, {"$set": {"borrowed": False}})

    # Update the book's return_date to datetime.now() in the database
    db.borrowings.update_one({"id": book_id}, {"$set": {"return_date": datetime.now()}})

    # Update the member's borrowed books list in the database
    db.members.update_one({"id": member_id}, {"$pull": {"borrowed_books": book_id}})

    return {"message": "Book returned successfully"}


   
    










if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)