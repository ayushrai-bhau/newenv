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

# GET /borrowings/{borrowingId} 
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

# POST /borrowings 
@router.post("/{book_id}/{member_id}")
async def borrow_book(book_id: str, member_id: str ,borrowing: Borrowing):
    
    book =  db.books.find_one({"id": book_id})
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    
    member =  db.members.find_one({"id": member_id})
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    if "borrowed" in book and book["borrowed"]:
        raise HTTPException(status_code=400, detail="Book is already borrowed")
     
    db.books.update_one({"id": book_id}, {"$set": {"borrowed": True}})


    db.members.update_one({"id": member_id}, {"$push": {"borrowed_books": book_id}})
    try:
        result = borrowings_collection.insert_one(borrowing.dict(by_alias=True))
        return {"message": "Book borrowed successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


