"""
config/config.py
Centralised configuration loader — reads from .env and provides
typed constants to the rest of the framework.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env from the project root (two levels up from this file)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    """All framework-wide constants live here. Import Config, not os.environ."""

    # ---- Network ----------------------------------------------------------
    BASE_URL: str = os.getenv("BASE_URL", "https://automationexercise.com/api")
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # ---- Auth -------------------------------------------------------------
    VALID_EMAIL: str = os.getenv("VALID_EMAIL", "testuser_siva@example.com")
    VALID_PASSWORD: str = os.getenv("VALID_PASSWORD", "Test@1234")

    # ---- Common headers ---------------------------------------------------
    DEFAULT_HEADERS: dict = {
        "Accept": "application/json",
    }

    # ---- Endpoints --------------------------------------------------------
    class Endpoints:
        PRODUCTS_LIST = "/productsList"
        BRANDS_LIST = "/brandsList"
        SEARCH_PRODUCT = "/searchProduct"
        VERIFY_LOGIN = "/verifyLogin"
        CREATE_ACCOUNT = "/createAccount"
        DELETE_ACCOUNT = "/deleteAccount"
        UPDATE_ACCOUNT = "/updateAccount"
        GET_USER_DETAIL = "/getUserDetailByEmail"

    # ---- HTTP Status Codes -----------------------------------------------
    class StatusCode:
        OK = 200
        CREATED = 201
        BAD_REQUEST = 400
        NOT_FOUND = 404
        METHOD_NOT_ALLOWED = 405
