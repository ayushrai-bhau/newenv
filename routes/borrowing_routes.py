from fastapi import APIRouter, HTTPException, status
from models.borrowing import Borrowing 
from db.mongodb import borrowings_collection
from bson import ObjectId
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/borrowings", tags=["Borrowings"])
MONGO_URI = os.getenv("DB_URL")

# Create a MongoClient instance
client = MongoClient(MONGO_URI)

# Get the database
db = client.get_database("LMS")



@router.get("/", response_model=list[Borrowing], status_code=status.HTTP_200_OK)
async def list_borrowings():
    """
    Get a list of all borrowings.

    Returns:
        list[Borrowing]: A list of borrowings.
    """
    borrowings = list(borrowings_collection.find({}))
    return [{"id": str(borrowing["_id"]), **borrowing} for borrowing in borrowings]

# GET /borrowings/{borrowingId} - Get details of a specific borrowing
@router.get("/{borrowingId}", response_model=Borrowing, status_code=status.HTTP_200_OK)
async def get_borrowing(borrowingId: str):
    """
    Get details of a specific borrowing.

    Parameters:
        borrowingId (str): The unique identifier of the borrowing.

    Returns:
        Borrowing: The borrowing object.

    Raises:
        HTTPException: If the borrowing is not found or if the provided borrowingId is invalid.
    """
    try:
        borrowing = borrowings_collection.find_one({"_id": ObjectId(borrowingId)})
        if borrowing:
            borrowing["id"] = str(borrowing.pop("_id"))
            return borrowing
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrowing not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# POST /borrowings - Create a new borrowing (check out a book)
@router.post("/{book_id}/{member_id}")
async def borrow_book(book_id: str, member_id: str ,borrowing: Borrowing):
    # Fetch the book from the database
    book =  db.books.find_one({"id": book_id})
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    # Fetch the member from the database
    member =  db.members.find_one({"id": member_id})
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    if "borrowed" in book and book["borrowed"]:
        raise HTTPException(status_code=400, detail="Book is already borrowed")
     # Update the book's borrowed status in the database
    db.books.update_one({"id": book_id}, {"$set": {"borrowed": True}})

    # Update the member's borrowed books list in the database
    db.members.update_one({"id": member_id}, {"$push": {"borrowed_books": book_id}})
    try:
        result = borrowings_collection.insert_one(borrowing.dict(by_alias=True))
        return {"message": "Book borrowed successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# PUT /borrowings/{borrowingId} - Update details of a borrowing (e.g., return date)
@router.put("/{borrowingId}", response_model=str, status_code=status.HTTP_200_OK)
async def update_borrowing(borrowingId: str, borrowing: Borrowing):
    """
    Update details of a borrowing (e.g., return date).

    Parameters:
        borrowingId (str): The unique identifier of the borrowing.
        borrowing (Borrowing): The updated borrowing object.

    Returns:
        str: A success message.

    Raises:
        HTTPException: If the borrowing is not found, if the provided borrowingId is invalid, or if there is an error while updating the borrowing.
    """
    try:
        result = borrowings_collection.update_one({"_id": ObjectId(borrowingId)}, {"$set": borrowing.dict(by_alias=True)})
        if result.modified_count == 1:
            return "Borrowing updated successfully"
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrowing not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# DELETE /borrowings/{borrowingId} - Delete a borrowing (when a book is returned)
@router.delete("/{borrowingId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_borrowing(borrowingId: str):
    """
    Delete a borrowing (when a book is returned).

    Parameters:
        borrowingId (str): The unique identifier of the borrowing.

    Returns:
        None
    """
    try:
        result = borrowings_collection.delete_one({"_id": ObjectId(borrowingId)})
        if result.deleted_count != 1:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrowing not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
