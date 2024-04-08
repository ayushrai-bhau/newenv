from pydantic import BaseModel, Field,validator
from typing import Optional
from datetime import datetime,timedelta

class Borrowing(BaseModel):
    id: str = Field(..., description="Unique identifier of the borrowing")
    book_id: str = Field(..., description="ID of the borrowed book")
    member_id: str = Field(..., description="ID of the member who borrowed the book")
    borrowed_date: datetime = Field(default_factory=datetime.now, description="Date when the book was borrowed")
    due_date: Optional[datetime] = Field(None, description="Due date for returning the book")
    return_date: Optional[datetime] = Field(None, description="Date when the book was returned")
    
    @validator("due_date", pre=True, always=True)
    def set_due_date(cls, v, values):
        if "borrowed_date" in values and values["borrowed_date"]:
            return values["borrowed_date"] + timedelta(days=14)
        return v