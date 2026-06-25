from pydantic import BaseModel


class ChatInput(BaseModel):
    chat_text: str
