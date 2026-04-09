"""
Application settings — loaded from .env or environment variables.
All fields have safe defaults so the app runs with zero configuration.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Server ────────────────────────────────────────────
    app_name: str = "BitMarket SV"
    app_version: str = "1.0.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    # ── Auth ──────────────────────────────────────────────
    # Safe default lets the app run without any .env file.
    # CHANGE THIS in production.
    secret_key: str = "dev-secret-key-change-in-production-please"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days

    # ── LNbits (optional) ─────────────────────────────────
    # Leave empty → mock mode activates automatically.
    # Mock invoices auto-confirm after MOCK_CONFIRM_SECONDS seconds.
    lnbits_url: str = ""
    lnbits_admin_key: str = ""
    invoice_expire_seconds: int = 600
    mock_confirm_seconds: int = 10  # seconds until mock payment confirms
    marketplace_fee_percent: float = 5.0

    # ── CORS ──────────────────────────────────────────────
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def lnbits_mock_mode(self) -> bool:
        """True when LNbits credentials are not set → safe fallback."""
        return not self.lnbits_url or not self.lnbits_admin_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
