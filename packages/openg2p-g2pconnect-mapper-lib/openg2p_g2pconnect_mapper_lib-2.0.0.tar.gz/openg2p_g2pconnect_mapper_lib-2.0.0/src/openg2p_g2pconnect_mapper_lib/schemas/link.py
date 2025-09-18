from datetime import datetime
from enum import Enum
from typing import List, Optional

from openg2p_g2pconnect_common_lib.schemas import Request, StatusEnum, SyncResponse
from pydantic import BaseModel


class SingleLinkRequest(BaseModel):
    reference_id: str
    timestamp: str
    id: str
    fa: str
    name: Optional[str] = None
    phone_number: Optional[str] = None
    additional_info: Optional[List[object]] = None
    locale: Optional[str] = "en"


class LinkRequestMessage(BaseModel):
    transaction_id: str
    link_request: List[SingleLinkRequest]


class LinkStatusReasonCode(Enum):
    rjct_reference_id_invalid = "rjct.reference_id.invalid"
    rjct_reference_id_duplicate = "rjct.reference_id.duplicate"
    rjct_timestamp_invalid = "rjct.timestamp.invalid"
    rjct_id_invalid = "rjct.id.invalid"
    rjct_fa_invalid = "rjct.fa.invalid"
    rjct_name_invalid = "rjct.name.invalid"
    rjct_mobile_number_invalid = "rjct.mobile_number.invalid"
    rjct_unknown_retry = "rjct.unknown.retry"
    rjct_other_error = "rjct.other.error"


class SingleLinkResponse(BaseModel):
    reference_id: str
    timestamp: datetime
    fa: Optional[str] = None
    status: StatusEnum
    status_reason_code: Optional[LinkStatusReasonCode] = None
    status_reason_message: Optional[str] = None
    additional_info: Optional[List[object]] = None
    locale: Optional[str] = "en"


class LinkResponseMessage(BaseModel):
    transaction_id: Optional[str] = None
    correlation_id: Optional[str] = None
    link_response: List[SingleLinkResponse]


class LinkResponse(SyncResponse):
    message: LinkResponseMessage


class LinkRequest(Request):
    message: LinkRequestMessage
