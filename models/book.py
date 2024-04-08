from pydantic import BaseModel, Field, EmailStr



class Book(BaseModel):
    id: str = Field(..., description="Unique identifier of the book")
    title: str = Field(..., description="Title of the book")
    author: str = Field(..., description="Author of the book")
    year: int = Field(..., description="Year of publication")
    genre: str = Field(None, description="Genre of the book")
    borrowed: bool = Field(False, description="Whether the book is currently borrowed")