from openg2p_fastapi_common.app import Initializer as BaseInitializer
from openg2p_fastapi_common.utils.crypto import KeymanagerCryptoHelper
from openg2p_g2pconnect_common_lib.jwt_validation_helper import JWTValidationHelper

from .client import (
    MapperLinkClient,
    MapperResolveClient,
    MapperUnlinkClient,
    MapperUpdateClient,
)


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        MapperLinkClient()
        MapperUpdateClient()
        MapperUnlinkClient()
        MapperResolveClient()
        JWTValidationHelper()
        KeymanagerCryptoHelper()
