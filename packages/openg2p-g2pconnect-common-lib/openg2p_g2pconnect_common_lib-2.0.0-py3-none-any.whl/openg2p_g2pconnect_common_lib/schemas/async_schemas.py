from datetime import datetime
from enum import Enum
from typing import Optional

from openg2p_fastapi_common.errors import ErrorResponse
from pydantic import AliasChoices, BaseModel, Field

from .status_codes import StatusEnum


class AsyncAck(Enum):
    ACK = "ACK"
    NACK = "NACK"
    ERR = "ERR"


class AsyncResponseStatusReasonCodeEnum(Enum):
    rjct_version_invalid = "rjct.version.invalid"
    rjct_message_id_duplicate = "rjct.message_id.duplicate"
    rjct_message_ts_invalid = "rjct.message_ts.invalid"
    rjct_action_invalid = "rjct.action.invalid"
    rjct_action_not_supported = "rjct.action.not_supported"
    rjct_total_count_invalid = "rjct.total_count.invalid"
    rjct_total_count_limit_exceeded = "rjct.total_count.limit_exceeded"
    rjct_errors_too_many = "rjct.errors.too_many"
    rjct_jwt_invalid = "rjct.jwt.invalid"


class AsyncResponseMessage(BaseModel):
    ack_status: Optional[AsyncAck] = None
    timestamp: datetime
    error: Optional[ErrorResponse] = None
    correlation_id: Optional[str] = None


class AsyncResponse(BaseModel):
    message: AsyncResponseMessage


class AsyncCallbackRequestHeader(BaseModel):
    version: str = "1.0.0"
    message_id: str
    message_ts: str
    action: str
    status: StatusEnum
    status_reason_code: Optional[AsyncResponseStatusReasonCodeEnum] = None
    status_reason_message: Optional[str] = None
    total_count: Optional[int] = 0
    completed_count: Optional[int] = 0
    sender_id: Optional[str] = None
    receiver_id: Optional[str] = None
    is_msg_encrypted: Optional[bool] = Field(
        validation_alias=AliasChoices("is_msg_encrypted", "is_encrypted"), default=False
    )
    meta: Optional[object] = None


class AsyncCallbackRequest(BaseModel):
    header: AsyncCallbackRequestHeader
    message: Optional[object] = None
