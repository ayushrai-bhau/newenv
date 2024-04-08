from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from fastapi import FastAPI, HTTPException

app = FastAPI()

class Book(BaseModel):
    id: str = Field(..., description="Unique identifier of the book")
    title: str = Field(..., description="Title of the book")
    author: str = Field(..., description="Author of the book")
    year: int = Field(..., description="Year of publication")
    genre: str = Field(None, description="Genre of the book")
    borrowed: bool = Field(False, description="Whether the book is currently borrowed")

class Member(BaseModel):
    id: str = Field(..., description="Unique identifier of the member")
    name: str = Field(..., description="Name of the member")
    email: EmailStr = Field(..., description="Email address of the member")
    phone: Optional[str] = Field(None, description="Phone number of the member")
    borrowed_books: List[str] = Field([], description="List of IDs of books borrowed by the member")

class Borrowing(BaseModel):
    
    book_id: str = Field(..., description="ID of the borrowed book")
    member_id: str = Field(..., description="ID of the member who borrowed the book")
    borrowed_date: datetime = Field(..., description="Date when the book was borrowed")
    due_date: Optional[datetime] = Field(None, description="Due date for returning the book")
    return_date: Optional[datetime] = Field(None, description="Date when the book was returned")

# Mock data for demonstration purposes
books = [
    Book(id="book1", title="Book 1", author="Author 1", year=2020),
    Book(id="book2", title="Book 2", author="Author 2", year=2021),
    Book(id="book3", title="Book 3", author="Author 3", year=2022),
]

members = [
    Member(id="member1", name="Member 1", email="member1@example.com"),
    Member(id="member2", name="Member 2", email="member2@example.com"),
]


@app.post("/borrow")
def borrow_book(borrowing: Borrowing):
    print("''''''''''''''''")
    book = next((b for b in books if b.id == borrowing.book_id), None)
    member = next((m for m in members if m.id == borrowing.member_id), None)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    if book.borrowed:
        raise HTTPException(status_code=400, detail="Book is already borrowed")

    book.borrowed = True
    member.borrowed_books.append(book.id)

    return {"message": "Book borrowed successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)