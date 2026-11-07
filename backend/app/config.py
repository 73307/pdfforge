"""Application settings.

Values come from environment variables (or a .env file). Everything has a safe
default so the app runs out of the box, but production should set these explicitly.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_debug: bool = False

    # Browser origins allowed to call this API (comma separated).
    cors_allow_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"

    # Upload / processing limits — defense in depth.
    max_upload_bytes: int = 52_428_800     # 50 MB whole request
    max_file_bytes: int = 26_214_400       # 25 MB per file
    max_files_per_request: int = 20
    max_pdf_pages: int = 500
    max_image_pixels: int = 40_000_000     # ~40 MP, guards against image bombs

    # Hard wall-clock timeout per processing operation (seconds).
    op_timeout_seconds: int = 30
    # Office conversions (LibreOffice / pdf2docx) are slower; give them more time.
    office_timeout_seconds: int = 120

    # Run each PDF operation in an isolated child process (recommended).
    # Tests disable this for speed/determinism.
    process_isolation: bool = True

    # Temp storage + retention.
    data_dir: str = ".data"
    retention_seconds: int = 900           # delete leftovers after 15 min
    download_token_ttl_seconds: int = 900

    # Per-IP rate limit.
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
