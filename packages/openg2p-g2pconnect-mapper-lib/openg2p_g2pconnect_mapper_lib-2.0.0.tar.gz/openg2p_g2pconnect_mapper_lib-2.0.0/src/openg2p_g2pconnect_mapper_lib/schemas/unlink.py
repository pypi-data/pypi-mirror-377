from datetime import datetime
from enum import Enum
from typing import List, Optional

from openg2p_g2pconnect_common_lib.schemas import Request, StatusEnum, SyncResponse
from pydantic import BaseModel


class UnlinkStatusReasonCode(Enum):
    rjct_reference_id_invalid = "rjct.reference_id.invalid"
    rjct_id_invalid = "rjct.id.invalid"
    rjct_fa_invalid = "rjct.fa.invalid"
    rjct_reference_id_duplicate = "rjct.reference_id.duplicate"
    rjct_timestamp_invalid = "rjct.timestamp.invalid"
    rjct_beneficiary_name_invalid = "rjct.beneficiary_name.invalid"


class SingleUnlinkRequest(BaseModel):
    reference_id: str
    timestamp: str
    id: str
    fa: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    additional_info: Optional[List[object]] = None
    locale: Optional[str] = "en"


class UnlinkRequestMessage(BaseModel):
    transaction_id: str
    unlink_request: List[SingleUnlinkRequest]


class SingleUnlinkResponse(BaseModel):
    reference_id: str
    timestamp: datetime
    id: Optional[str] = ""
    status: StatusEnum
    status_reason_code: Optional[UnlinkStatusReasonCode] = None
    status_reason_message: Optional[str] = ""
    additional_info: Optional[List[object]] = None
    locale: Optional[str] = "en"


class UnlinkResponseMessage(BaseModel):
    transaction_id: Optional[str] = None
    correlation_id: Optional[str] = ""
    unlink_response: List[SingleUnlinkResponse]


class UnlinkRequest(Request):
    message: UnlinkRequestMessage


class UnlinkResponse(SyncResponse):
    message: UnlinkResponseMessage
