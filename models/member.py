from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Member(BaseModel):
    id: str = Field(..., description="Unique identifier of the member")
    name: str = Field(..., description="Name of the member")
    email: EmailStr = Field(..., description="Email address of the member")
    phone: Optional[str] = Field(None, description="Phone number of the member")