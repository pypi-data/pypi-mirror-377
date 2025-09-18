from typing import Optional

from pydantic import AliasChoices, BaseModel, Field


class RequestHeader(BaseModel):
    version: Optional[str] = "1.0.0"
    message_id: str
    message_ts: str
    action: str
    sender_id: str
    sender_uri: Optional[str] = ""
    receiver_id: Optional[str] = ""
    total_count: int
    is_msg_encrypted: Optional[bool] = Field(
        validation_alias=AliasChoices("is_msg_encrypted", "is_encrypted"), default=False
    )
    meta: Optional[object] = None


class Request(BaseModel):
    header: RequestHeader
    message: object
