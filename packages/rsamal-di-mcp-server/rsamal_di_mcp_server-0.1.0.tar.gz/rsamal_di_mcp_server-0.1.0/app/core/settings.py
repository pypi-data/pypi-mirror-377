from pydantic import AnyHttpUrl
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from app.shared.models.ssl_config import SSLConfig


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields like old TOKEN setting
    )

    # HTTP Client Settings
    request_timeout_s: int = 10
    base_url: AnyHttpUrl | str | None = None

    # Saas IAM url
    cloud_iam_url: AnyHttpUrl | str | None = None

    # SSL Configuration (enhanced certificate support)
    ssl_config: SSLConfig = SSLConfig()

    # Backwards compatibility - deprecated, use ssl_config instead
    ssl_verify: bool = True  # Set to False for self-signed certificates

    # MCP Server Settings
    server_host: str = "0.0.0.0"
    server_port: int = 3000
    server_transport: str = "http"  # "http" or "stdio"

    # Auth token for stdio mode (optional)
    stdio_auth_token: str | None = None

    # Auth apikey for stdio mode(optional)
    stdio_apikey: str | None = None
    # username for CPD
    stdio_username: str | None = None

    #CPD, SaaS
    env_mode: str | None = None

    # Log file path
    log_file_path: str | None = None

    def get_auth_config(self) -> dict:
        """Get authentication configuration for the current auth mode."""
        return {
            "mode": self.auth_mode,
            "iam_url": self.auth_iam_url,
            "wkc_service_id": self.auth_wkc_service_id,
            "auto_error": self.auth_auto_error,
        }


settings = Settings()
