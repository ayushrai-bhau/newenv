from fastapi import APIRouter, HTTPException, status
from models.member import Member
from db.mongodb import members_collection
from bson import ObjectId
from pymongo import IndexModel, ASCENDING

router = APIRouter(prefix="/members", tags=["Members"])
@router.get("/", response_model=list[Member], status_code=status.HTTP_200_OK)
async def list_members():
    """
    Get a list of all members.

    Returns:
        list[Member]: A list of members.
    """
    members = list(members_collection.find({}))
    return [{"id": str(member["_id"]), **member} for member in members]

# GET /members/{memberId} - Get details of a specific member
@router.get("/{memberId}", response_model=Member, status_code=status.HTTP_200_OK)
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

 


@router.post("/", response_model=str, status_code=status.HTTP_201_CREATED)
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
    

# PUT /members/{memberId} - Update details of a member
@router.put("/{memberId}", response_model=str, status_code=status.HTTP_200_OK)
async def update_member(memberId: str, member: Member):
    """
    Update details of a member.

    Parameters:
        memberId (str): The unique identifier of the member.
        member (Member): The updated member object.

    Returns:
        str: A success message.

    Raises:
        HTTPException: If the member is not found, if the provided memberId is invalid, or if there is an error while updating the member.
    """
    try:
        result = members_collection.update_one({"_id": ObjectId(memberId)}, {"$set": member.dict(by_alias=True)})
        if result.modified_count == 1:
            return "Member updated successfully"
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# DELETE /members/{memberId} - Remove a member
@router.delete("/{memberId}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(memberId: str):
    """
    Remove a member.

    Parameters:
        memberId (str): The unique identifier of the member.

    Returns:
        None

    Raises:
        HTTPException: If the member is not found, if the provided memberId is invalid, or if there is an error while removing the member.
    """
    try:
        result = members_collection.delete_one({"_id": ObjectId(memberId)})
        if result.deleted_count == 1:
            return
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
