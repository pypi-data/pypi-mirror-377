from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openg2p_fastapi_common.utils.crypto import CryptoHelper
from openg2p_g2pconnect_common_lib.jwt_validation_helper import JWTValidationHelper
from openg2p_g2pconnect_common_lib.schemas import StatusEnum
from openg2p_g2pconnect_common_lib.schemas.requests import RequestHeader
from openg2p_g2pconnect_common_lib.schemas.sync_schemas import SyncResponseHeader
from openg2p_g2pconnect_mapper_lib.client import (
    MapperLinkClient,
    MapperResolveClient,
    MapperUnlinkClient,
    MapperUpdateClient,
)
from openg2p_g2pconnect_mapper_lib.schemas import (
    LinkRequest,
    LinkResponse,
    ResolveRequest,
    ResolveResponse,
    SingleLinkRequest,
    SingleResolveRequest,
    SingleUnlinkRequest,
    SingleUpdateRequest,
    UnlinkRequest,
    UnlinkResponse,
    UpdateRequest,
    UpdateResponse,
)
from openg2p_g2pconnect_mapper_lib.schemas.link import (
    LinkRequestMessage,
    LinkResponseMessage,
    SingleLinkResponse,
)
from openg2p_g2pconnect_mapper_lib.schemas.resolve import (
    ResolveRequestMessage,
    ResolveResponseMessage,
    SingleResolveResponse,
)
from openg2p_g2pconnect_mapper_lib.schemas.unlink import (
    SingleUnlinkResponse,
    UnlinkRequestMessage,
    UnlinkResponseMessage,
)
from openg2p_g2pconnect_mapper_lib.schemas.update import (
    SingleUpdateResponse,
    UpdateRequestMessage,
    UpdateResponseMessage,
)


@pytest.fixture()
def setup_link():
    mock_link_response = LinkResponse(
        header=SyncResponseHeader(
            message_id="test_message_id",
            message_ts=datetime.now().isoformat(),
            action="link",
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message="Success",
        ),
        message=LinkResponseMessage(
            transaction_id="trans_id",
            link_response=[
                SingleLinkResponse(
                    reference_id="test_ref",
                    timestamp=datetime.now(),
                    status=StatusEnum.succ,
                    additional_info=[{}],
                    fa="test_fa",
                    status_reason_code=None,
                    status_reason_message="Test message",
                    locale="en",
                )
            ],
        ),
    )
    response_json = {
        "header": {
            "message_id": "test_message_id",
            "message_ts": datetime.now().isoformat(),
            "action": "link",
            "status": "succ",
            "status_reason_code": None,
            "status_reason_message": "Success",
        },
        "message": {
            "transaction_id": "trans_id",
            "link_response": [
                {
                    "reference_id": "test_ref",
                    "timestamp": datetime.now().isoformat(),
                    "status": "succ",
                    "additional_info": [{}],
                    "fa": "test_fa",
                    "status_reason_code": None,
                    "status_reason_message": "Test message",
                    "locale": "en",
                }
            ],
        },
    }

    mock_link_request = LinkRequest(
        header=RequestHeader(
            message_id="test_message_id",
            message_ts=datetime.now().isoformat(),
            action="test_action",
            sender_id="test_sender",
            total_count=1,
        ),
        message=LinkRequestMessage(
            transaction_id="test_transaction_id",
            link_request=[
                SingleLinkRequest(
                    reference_id="test_ref",
                    timestamp=str(datetime.now()),
                    id="test_id",
                    fa="test_fa",
                )
            ],
        ),
    )
    JWTValidationHelper()
    CryptoHelper()
    return mock_link_response, mock_link_request, response_json


@pytest.mark.asyncio
async def test_link_request_successful(setup_link):
    mock_link_response, mock_link_request, response_json = setup_link

    with (
        patch(
            "openg2p_g2pconnect_mapper_lib.client.link.httpx.AsyncClient.post", new_callable=AsyncMock
        ) as mock_post,
        patch("openg2p_fastapi_common.utils.crypto.CryptoHelper.create_jwt_token") as mock_create_jwt,
    ):
        mock_post.return_value.json = MagicMock(return_value=response_json)
        mock_create_jwt.return_value = "mock_jwt"

        mapper_service = MapperLinkClient()
        link_response = await mapper_service.link_request(mock_link_request)

        assert link_response.header.message_id == mock_link_response.header.message_id
        assert isinstance(link_response, LinkResponse)


@pytest.fixture()
def setup_update():
    mock_update_response = UpdateResponse(
        header=SyncResponseHeader(
            message_id="test_message_id",
            message_ts=datetime.now().isoformat(),
            action="update",
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message="Success",
        ),
        message=UpdateResponseMessage(
            transaction_id="trans_id",
            update_response=[
                SingleUpdateResponse(
                    reference_id="test_ref",
                    timestamp=datetime.now(),
                    status=StatusEnum.succ,
                    additional_info=[{}],
                    fa="test_fa",
                    status_reason_code=None,
                    status_reason_message="Test message",
                    locale="en",
                )
            ],
        ),
    )
    response_json = {
        "header": {
            "message_id": "test_message_id",
            "message_ts": datetime.now().isoformat(),
            "action": "update",
            "status": "succ",
            "status_reason_code": None,
            "status_reason_message": "Success",
        },
        "message": {
            "transaction_id": "trans_id",
            "update_response": [
                {
                    "reference_id": "test_ref",
                    "timestamp": datetime.now().isoformat(),
                    "status": "succ",
                    "additional_info": [{}],
                    "fa": "test_fa",
                    "status_reason_code": None,
                    "status_reason_message": "Test message",
                    "locale": "en",
                }
            ],
        },
    }
    mock_update_request = UpdateRequest(
        header=RequestHeader(
            message_id="test_message_id",
            message_ts=datetime.now().isoformat(),
            action="test_action",
            sender_id="test_sender",
            total_count=1,
        ),
        message=UpdateRequestMessage(
            transaction_id="test_transaction_id",
            update_request=[
                SingleUpdateRequest(
                    reference_id="test_ref",
                    timestamp=str(datetime.now()),
                    id="test_id",
                    fa="test_fa",
                )
            ],
        ),
    )
    return mock_update_response, mock_update_request, response_json


@pytest.mark.asyncio
async def test_update_request_successful(setup_update):
    mock_update_response, mock_update_request, response_json = setup_update
    with (
        patch(
            "openg2p_g2pconnect_mapper_lib.client.link.httpx.AsyncClient.post", new_callable=AsyncMock
        ) as mock_post,
        patch("openg2p_fastapi_common.utils.crypto.CryptoHelper.create_jwt_token") as mock_create_jwt,
    ):
        mock_post.return_value.json = MagicMock(return_value=response_json)
        mock_create_jwt.return_value = "mock_jwt"

        mapper_service = MapperUpdateClient()
        update_response = await mapper_service.update_request(mock_update_request)
        assert update_response.header.message_id == mock_update_response.header.message_id
        assert isinstance(update_response, UpdateResponse)


@pytest.fixture()
def setup_resolve():
    mock_resolve_response = ResolveResponse(
        header=SyncResponseHeader(
            message_id="test_message_id",
            message_ts=datetime.now().isoformat(),
            action="resolve",
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message="Success",
        ),
        message=ResolveResponseMessage(
            transaction_id="trans_id",
            resolve_response=[
                SingleResolveResponse(
                    reference_id="test_ref",
                    timestamp=datetime.now(),
                    status=StatusEnum.succ,
                    additional_info=[{}],
                    fa="test_fa",
                    status_reason_code=None,
                    status_reason_message="Test message",
                    locale="en",
                )
            ],
        ),
    )
    response_json = {
        "header": {
            "message_id": "test_message_id",
            "message_ts": datetime.now().isoformat(),
            "action": "resolve",
            "status": "succ",
            "status_reason_code": None,
            "status_reason_message": "Success",
        },
        "message": {
            "transaction_id": "trans_id",
            "resolve_response": [
                {
                    "reference_id": "test_ref",
                    "timestamp": datetime.now().isoformat(),
                    "status": "succ",
                    "additional_info": [{}],
                    "fa": "test_fa",
                    "status_reason_code": None,
                    "status_reason_message": "Test message",
                    "locale": "en",
                }
            ],
        },
    }
    mock_resolve_request = ResolveRequest(
        header=RequestHeader(
            message_id="test_message_id",
            message_ts=datetime.now().isoformat(),
            action="test_action",
            sender_id="test_sender",
            total_count=1,
        ),
        message=ResolveRequestMessage(
            transaction_id="test_transaction_id",
            resolve_request=[
                SingleResolveRequest(
                    reference_id="test_ref",
                    timestamp=str(datetime.now()),
                    id="test_id",
                    fa="test_fa",
                )
            ],
        ),
    )
    return mock_resolve_response, mock_resolve_request, response_json


@pytest.mark.asyncio
async def test_resolve_request_successful(setup_resolve):
    mock_resolve_response, mock_resolve_request, response_json = setup_resolve
    with (
        patch(
            "openg2p_g2pconnect_mapper_lib.client.link.httpx.AsyncClient.post", new_callable=AsyncMock
        ) as mock_post,
        patch("openg2p_fastapi_common.utils.crypto.CryptoHelper.create_jwt_token") as mock_create_jwt,
    ):
        mock_post.return_value.json = MagicMock(return_value=response_json)
        mock_create_jwt.return_value = "mock_jwt"

        mapper_service = MapperResolveClient()
        resolve_response = await mapper_service.resolve_request(mock_resolve_request)
        assert resolve_response.header.message_id == mock_resolve_response.header.message_id
        assert isinstance(resolve_response, ResolveResponse)


@pytest.fixture()
def setup_unlink():
    mock_unlink_response = UnlinkResponse(
        header=SyncResponseHeader(
            message_id="test_message_id",
            message_ts=datetime.now().isoformat(),
            action="unlink",
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message="Success",
        ),
        message=UnlinkResponseMessage(
            transaction_id="trans_id",
            unlink_response=[
                SingleUnlinkResponse(
                    reference_id="test_ref",
                    timestamp=datetime.now(),
                    status=StatusEnum.succ,
                    additional_info=[{}],
                    fa="test_fa",
                    status_reason_code=None,
                    status_reason_message="Test message",
                    locale="en",
                )
            ],
        ),
    )
    response_json = {
        "header": {
            "message_id": "test_message_id",
            "message_ts": datetime.now().isoformat(),
            "action": "unlink",
            "status": "succ",
            "status_reason_code": None,
            "status_reason_message": "Success",
        },
        "message": {
            "transaction_id": "trans_id",
            "unlink_response": [
                {
                    "reference_id": "test_ref",
                    "timestamp": datetime.now().isoformat(),
                    "status": "succ",
                    "additional_info": [{}],
                    "fa": "test_fa",
                    "status_reason_code": None,
                    "status_reason_message": "Test message",
                    "locale": "en",
                }
            ],
        },
    }
    mock_unlink_request = UnlinkRequest(
        header=RequestHeader(
            message_id="test_message_id",
            message_ts=datetime.now().isoformat(),
            action="test_action",
            sender_id="test_sender",
            total_count=1,
        ),
        message=UnlinkRequestMessage(
            transaction_id="test_transaction_id",
            unlink_request=[
                SingleUnlinkRequest(
                    reference_id="test_ref",
                    timestamp=str(datetime.now()),
                    id="test_id",
                    fa="test_fa",
                )
            ],
        ),
    )
    return mock_unlink_response, mock_unlink_request, response_json


@pytest.mark.asyncio
async def test_unlink_request_successful(setup_unlink):
    mock_unlink_response, mock_unlink_request, response_json = setup_unlink
    with (
        patch(
            "openg2p_g2pconnect_mapper_lib.client.link.httpx.AsyncClient.post", new_callable=AsyncMock
        ) as mock_post,
        patch("openg2p_fastapi_common.utils.crypto.CryptoHelper.create_jwt_token") as mock_create_jwt,
    ):
        mock_post.return_value.json = MagicMock(return_value=response_json)
        mock_create_jwt.return_value = "mock_jwt"

        mapper_service = MapperUnlinkClient()
        unlink_response = await mapper_service.unlink_request(mock_unlink_request)
        assert unlink_response.header.message_id == mock_unlink_response.header.message_id
        assert isinstance(unlink_response, UnlinkResponse)
