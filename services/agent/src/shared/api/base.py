# 1st party
from typing import Optional

# 3rd aprty
from pydantic import BaseModel


class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None


class Chat(BaseModel):
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class Message(BaseModel):
    message_id: int
    from_user: Optional[User] = None
    chat: Chat
    date: int
    text: Optional[str] = None


class CallbackQuery(BaseModel):
    id: str
    from_user: User
    message: Optional[Message] = None
    inline_message_id: Optional[str] = None
    chat_instance: str
    data: Optional[str] = None


class UpdateTelegram(BaseModel):
    update_id: int
    message: Optional[Message] = None


class SearchEngineQuery(BaseModel):
    query: str


class SearchEngineQueryCoord(SearchEngineQuery):
    long: float
    lat: float
    distance: int
