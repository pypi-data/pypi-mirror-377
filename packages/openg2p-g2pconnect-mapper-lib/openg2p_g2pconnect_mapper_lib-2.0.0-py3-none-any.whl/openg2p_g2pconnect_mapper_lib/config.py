from openg2p_g2pconnect_common_lib.config import Settings as BaseSettings
from pydantic import model_validator
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="g2pconnect_", env_file=".env", extra="allow")

    mapper_client_api_base_url: str = "http://localhost:8007/sync"

    mapper_link_client_path: str = "/link"
    mapper_link_client_url: str = ""
    mapper_link_client_api_timeout: int = 60
    mapper_link_client_api_sign_enabled: bool = True
    mapper_link_client_crypto_helper_name: str = ""

    mapper_update_client_path: str = "/update"
    mapper_update_client_url: str = ""
    mapper_update_client_api_timeout: int = 60
    mapper_update_client_api_sign_enabled: bool = True
    mapper_update_client_crypto_helper_name: str = ""

    mapper_resolve_client_path: str = "/resolve"
    mapper_resolve_client_url: str = ""
    mapper_resolve_client_api_timeout: int = 60
    mapper_resolve_client_api_sign_enabled: bool = True
    mapper_resolve_client_crypto_helper_name: str = ""

    mapper_unlink_client_path: str = "/unlink"
    mapper_unlink_client_url: str = ""
    mapper_unlink_client_api_timeout: int = 60
    mapper_unlink_client_api_sign_enabled: bool = True
    mapper_unlink_client_crypto_helper_name: str = ""

    @model_validator(mode="after")
    def validate_mapper_configs(self):
        base_url = self.mapper_client_api_base_url.rstrip("/")
        if not self.mapper_link_client_url:
            self.mapper_link_client_url = "/".join([base_url, self.mapper_link_client_path.lstrip("/")])
        if not self.mapper_update_client_url:
            self.mapper_update_client_url = "/".join([base_url, self.mapper_update_client_path.lstrip("/")])
        if not self.mapper_resolve_client_url:
            self.mapper_resolve_client_url = "/".join([base_url, self.mapper_resolve_client_path.lstrip("/")])
        if not self.mapper_unlink_client_url:
            self.mapper_unlink_client_url = "/".join([base_url, self.mapper_unlink_client_path.lstrip("/")])
        return self
