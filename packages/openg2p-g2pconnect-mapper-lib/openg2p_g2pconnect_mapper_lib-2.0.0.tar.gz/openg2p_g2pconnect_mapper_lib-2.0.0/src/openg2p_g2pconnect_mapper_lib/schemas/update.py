from datetime import datetime
from enum import Enum
from typing import List, Optional

from openg2p_g2pconnect_common_lib.schemas import Request, StatusEnum, SyncResponse
from pydantic import BaseModel


class UpdateStatusReasonCode(Enum):
    rjct_reference_id_invalid = "rjct.reference_id.invalid"
    rjct_reference_id_duplicate = "rjct.reference_id.duplicate"
    rjct_timestamp_invalid = "rjct.timestamp.invalid"
    rjct_beneficiary_name_invalid = "rjct.beneficiary_name.invalid"
    rjct_id_invalid = "rjct.id.invalid"
    rjct_fa_invalid = "rjct.fa.invalid"


class SingleUpdateRequest(BaseModel):
    reference_id: str
    timestamp: str
    id: str
    fa: str
    name: Optional[str] = None
    phone_number: Optional[str] = None
    additional_info: Optional[List[object]] = None
    locale: Optional[str] = "en"


class UpdateRequestMessage(BaseModel):
    transaction_id: str
    update_request: List[SingleUpdateRequest]


class SingleUpdateResponse(BaseModel):
    reference_id: str
    timestamp: datetime
    id: Optional[str] = ""
    status: StatusEnum
    status_reason_code: Optional[UpdateStatusReasonCode] = None
    status_reason_message: Optional[str] = ""
    additional_info: Optional[List[object]] = None
    locale: Optional[str] = "en"


class UpdateResponseMessage(BaseModel):
    transaction_id: Optional[str] = None
    correlation_id: Optional[str] = ""
    update_response: List[SingleUpdateResponse]


class UpdateRequest(Request):
    message: UpdateRequestMessage


class UpdateResponse(SyncResponse):
    message: UpdateResponseMessage
