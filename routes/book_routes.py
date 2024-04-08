from fastapi import APIRouter, HTTPException, status
from models.book import Book
from db.mongodb import books_collection
from bson import ObjectId
from pymongo import IndexModel, ASCENDING



router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[Book], status_code=status.HTTP_200_OK)
async def list_books():
    """
    Get a list of all books.

    Returns:
        list[Book]: A list of books.
    """
    print("/////////")
    books = list(books_collection.find({}))  # Include _id in the result
    return [{"id": str(book["_id"]), **book} for book in books]


# GET /books/{bookId} - Get details of a specific book
@router.get("/{bookId}", response_model=Book, status_code=status.HTTP_200_OK)
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

@router.post("/", response_model=str, status_code=status.HTTP_201_CREATED)
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
@router.put("/{bookId}", response_model=str, status_code=status.HTTP_200_OK)
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

@router.delete("/{bookId}", status_code=status.HTTP_200_OK)
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
