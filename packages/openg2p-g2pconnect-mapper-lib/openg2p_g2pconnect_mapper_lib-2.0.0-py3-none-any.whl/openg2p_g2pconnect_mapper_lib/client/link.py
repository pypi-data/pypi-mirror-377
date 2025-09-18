import logging
from functools import cached_property

import httpx
import orjson
from openg2p_fastapi_common.errors.base_exception import BaseAppException
from openg2p_fastapi_common.service import BaseService
from openg2p_fastapi_common.utils.crypto import CryptoHelper

from ..config import Settings
from ..schemas import LinkRequest, LinkResponse

_config = Settings.get_config(strict=False)
_logger = logging.getLogger(_config.logging_default_logger_name)


class MapperLinkClient(BaseService):
    def __init__(
        self,
        url: str = _config.mapper_link_client_url,
        api_timeout: int = _config.mapper_link_client_api_timeout,
        api_sign_enabled: bool = _config.mapper_link_client_api_sign_enabled,
        api_sign_crypto_helper_name: str = _config.mapper_link_client_crypto_helper_name,
        **kw,
    ):
        super().__init__(**kw)
        self.url = url
        self.api_timeout = api_timeout
        self.api_sign_enabled = api_sign_enabled
        self.api_sign_crypto_helper_name = api_sign_crypto_helper_name

        self.http_client = httpx.AsyncClient(timeout=self.api_timeout)

    @cached_property
    def crypto_helper(self):
        return CryptoHelper.get_component(name=self.api_sign_crypto_helper_name)

    async def link_request(self, request: LinkRequest, headers: dict | None = None) -> LinkResponse:
        try:
            payload = request.model_dump(mode="json")

            orig_headers = {"content-type": "application/json"}
            if self.api_sign_enabled:
                orig_headers["Signature"] = await self.crypto_helper.create_jwt_token(payload)
            if headers:
                orig_headers.update(headers)

            res = await self.http_client.post(
                self.url,
                content=orjson.dumps(payload, option=orjson.OPT_SORT_KEYS),
                headers=orig_headers,
            )
            res.raise_for_status()
            return LinkResponse.model_validate(res.json())
        except httpx.HTTPStatusError as e:
            _logger.exception("Http Error in link request")
            raise BaseAppException(
                message="Error in link request",
                code=str(e.response.status_code),
            ) from e
        except Exception as e:
            _logger.exception("Unknown Error in link request")
            raise BaseAppException(
                message="Unknown Error in link request",
                code="500",
            ) from e
