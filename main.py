from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from pymongo import MongoClient,IndexModel, ASCENDING
from bson import ObjectId
from typing import Optional


# MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://jhonwatson172:W07hvLnwpfYvRveM@lms.jmir4fk.mongodb.net/?retryWrites=true&w=majority&appName=LMS"

# Create a MongoClient instance
client = MongoClient(MONGO_URI)

# Get the database~
db = client.get_database("LMS")

# Get the books collection
books_collection = db.books
members_collection = db.members

# Create a FastAPI instance
app = FastAPI()

# Pydantic model for Book
class Book(BaseModel):
    id: str = Field(..., description="Unique identifier of the book")
    title: str = Field(..., description="Title of the book")
    author: str = Field(..., description="Author of the book")
    year: int = Field(..., description="Year of publication")
    genre: Optional[str] = Field(None, description="Genre of the book")



class Member(BaseModel):
    id: str = Field(..., description="Unique identifier of the member")
    name: str = Field(..., description="Name of the member")
    email: EmailStr = Field(..., description="Email address of the member")
    phone: Optional[str] = Field(None, description="Phone number of the member")



@app.get("/members", response_model=list[Member], status_code=status.HTTP_200_OK)
async def list_members():
    """
    Get a list of all members.

    Returns:
        list[Member]: A list of members.
    """
    members = list(members_collection.find({}))
    return [{"id": str(member["_id"]), **member} for member in members]

@app.get("/members/{memberId}", response_model=Member, status_code=status.HTTP_200_OK)
async def get_member(memberId: str):
    """
    Get details of a specific member.

    Parameters:
        memberId (str): The unique identifier of the member.

    Returns:
        Member: The member object.

    Raises:
        HTTPException: If the member is not found or if the provided memberId is invalid.
    """
    try:
        member = members_collection.find_one({"_id": ObjectId(memberId)} )
        if member is not None:
            member["id"] = str(member.pop("_id"))
            return member
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

 


@app.post("/members", response_model=str, status_code=status.HTTP_201_CREATED)
async def add_member(member: Member):
    """
    Add a new member.

    Parameters:
        member (Member): The member object to be added.

    Returns:
        str: The unique identifier of the added member.

    Raises:
        HTTPException: If there is an error while adding the member.
    """
    try:
        result = members_collection.insert_one(member.dict(by_alias=True))
        return str(result.inserted_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



# GET /books - Get a list of all books
@app.get("/books", response_model=list[Book], status_code=status.HTTP_200_OK)
async def list_books():
    """
    Get a list of all books.

    Returns:
        list[Book]: A list of books.
    """
    books = list(books_collection.find({}))  # Include _id in the result
    return [{"id": str(book["_id"]), **book} for book in books]





# GET /books/{bookId} - Get details of a specific book
@app.get("/books/{bookId}", response_model=Book, status_code=status.HTTP_200_OK)
async def get_book(bookId: str):
    """
    Get details of a specific book.

    Parameters:
        bookId (str): The unique identifier of the book.

    Returns:
        Book: The book object.

    Raises:
        HTTPException: If the book is not found or if the provided bookId is invalid.
    """
    try:
        book = books_collection.find_one({"_id": ObjectId(bookId)})
        if book is not None:
            book["id"] = str(book.pop("_id"))
            return book
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# POST /books - Add a new book
index_model = IndexModel([("id", ASCENDING)], unique=True)
books_collection.create_indexes([index_model])

@app.post("/books", response_model=str, status_code=status.HTTP_201_CREATED)
async def add_book(book: Book):
    """
    Add a new book.

    Parameters:
        book (Book): The book object to be added.

    Returns:
        str: A success message along with the unique identifier of the added book.

    Raises:
        HTTPException: If there is an error while adding the book.
    """
    try:
        result = books_collection.insert_one(book.dict(by_alias=True))
        return f"Book with ID {result.inserted_id} created successfully"
    except Exception as e:
        # Check if the error is due to a duplicate key violation
        if "E11000" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book with the same ID or title already exists")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



# PUT /books/{bookId} - Update details of a book
@app.put("/books/{bookId}", response_model=str, status_code=status.HTTP_200_OK)
async def update_book(bookId: str, book: Book):
    """
    Update details of a book.

    Parameters:
        bookId (str): The unique identifier of the book.
        book (Book): The updated book object.

    Returns:
        str: A success message.

    Raises:
        HTTPException: If the book is not found, if the provided bookId is invalid, or if there is an error while updating the book.
    """
    try:
        result = books_collection.update_one({"_id": ObjectId(bookId)}, {"$set": book.dict(by_alias=True)})
        if result.modified_count == 1:
            return "Book updated successfully"
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

from fastapi.responses import JSONResponse

@app.delete("/books/{bookId}", status_code=status.HTTP_200_OK)
async def remove_book(bookId: str):
    """
    Remove a book.

    Parameters:
        bookId (str): The unique identifier of the book.

    Returns:
        dict: A JSON object containing a success message indicating that the book was deleted successfully.

    Raises:
        HTTPException: If the book is not found, if the provided bookId is invalid, or if there is an error while removing the book.
    """
    try:
        result = books_collection.delete_one({"_id": ObjectId(bookId)})
        if result.deleted_count != 1:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        return JSONResponse(content={"message": "Book deleted successfully"})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)