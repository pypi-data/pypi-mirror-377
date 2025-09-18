from enum import Enum
from typing import List, Optional

from openg2p_g2pconnect_common_lib.schemas import Request, SyncResponse
from pydantic import BaseModel


class TxnStatusReasonCode(Enum):
    rjct_reference_id_invalid = "rjct.reference_id.invalid"
    rjct_reference_id_duplicate = "rjct.reference_id.duplicate"
    rjct_timestamp_invalid = "rjct.timestamp.invalid"
    rjct_beneficiary_name_invalid = "rjct.beneficiary_name.invalid"
    rjct_id_invalid = "rjct.id.invalid"


class TxnAttributeType(Enum):
    transaction_id = "transaction_id"
    reference_id_list = "reference_id_list"
    correlation_id = "correlation_id"


class TxnType(Enum):
    link = "link"
    unlink = "unlink"
    resolve = "resolve"
    update = "update"


class SingleTxnStatusRequest(BaseModel):
    reference_id: str
    timestamp: str
    txn_type: TxnType
    attribute_type: TxnAttributeType
    attribute_value: str
    locale: Optional[str] = "en"


class TxnStatusRequestMessage(BaseModel):
    transaction_id: str
    txnstatus_request: List[SingleTxnStatusRequest]


class SingleTxnStatusResponse(BaseModel):
    txn_type: TxnType
    txn_status: dict


class TxnStatusResponseMessage(BaseModel):
    transaction_id: str
    correlation_id: Optional[str] = ""
    txnstatus_response: List[SingleTxnStatusResponse]


class TxnStatusRequest(Request):
    message: TxnStatusRequestMessage


class TxnStatusResponse(SyncResponse):
    message: TxnStatusResponseMessage
