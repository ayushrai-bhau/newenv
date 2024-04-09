from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from pymongo import MongoClient
from datetime import datetime


from .routes import book_routes,member_routes,borrowing_routes




import os
from dotenv import load_dotenv
load_dotenv()



MONGO_URI = os.getenv("DB_URL")


client = MongoClient(MONGO_URI)


db = client.get_database("LMS")


books_collection = db.books
members_collection = db.members


app = FastAPI()

app.include_router(book_routes.router)
app.include_router(member_routes.router)
app.include_router(borrowing_routes.router)


@app.post("/return/{book_id}/{member_id}")
async def return_book(book_id: str, member_id: str):
    
    book =  db.books.find_one({"id": book_id})
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    
    member =  db.members.find_one({"id": member_id})
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    if book["borrowed"] is False:
        raise HTTPException(status_code=400, detail="Book is not borrowed")

    if book_id not in member["borrowed_books"]:
        raise HTTPException(status_code=400, detail="Book is not borrowed by the member")

    
    db.books.update_one({"id": book_id}, {"$set": {"borrowed": False}})

    
    db.borrowings.update_one({"id": book_id}, {"$set": {"return_date": datetime.now()}})

    db.members.update_one({"id": member_id}, {"$pull": {"borrowed_books": book_id}})

    return {"message": "Book returned successfully"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)