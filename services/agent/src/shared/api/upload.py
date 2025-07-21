# 1st party
from typing import Optional

# 3rd party
from fastapi import APIRouter, Header, HTTPException
from starlette import status

# internal libs
from src.config import config
from src.services.load_restaurants.upload_place import GetUploadPlace

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/restaurant/{place_name}")
def upload_restaurant(
    place_name: str, x_telegram_bot_api_secret_token: Optional[str] = Header(None)
):
    """
    Upload restaurant to vector store
    """
    if x_telegram_bot_api_secret_token != config.secret_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect secret_token"
        )
    GetUploadPlace().get_upload_places_by_name(place_name)
    return {"message": f"Place '{place_name}' uploaded successfully."}