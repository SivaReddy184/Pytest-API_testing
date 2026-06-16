"""
conftest.py
Shared pytest fixtures available to the entire test suite.
Fixtures here follow a strict scope hierarchy:
  session  → created once per `pytest` invocation
  module   → once per test file
  function → default; fresh per test
"""

import logging
import uuid

import pytest

from config.config import Config
from utils.api_client import APIClient
from utils.assertions import APIAssertions
from data.test_data import new_user_payload

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Session-scoped: one APIClient for the entire run (connection pool reuse)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def api_client() -> APIClient:
    """
    A single APIClient instance shared across all tests.
    Closes the underlying session when the run is complete.
    """
    client = APIClient()
    logger.info("APIClient session opened — base URL: %s", Config.BASE_URL)
    yield client
    client.close()
    logger.info("APIClient session closed.")


# ---------------------------------------------------------------------------
# Assertion helper (stateless — no teardown needed)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def assert_api() -> APIAssertions:
    return APIAssertions()


# ---------------------------------------------------------------------------
# Managed user fixture — creates a user before the test, deletes after
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def managed_user(api_client: APIClient):
    """
    Creates a fresh user account before the test yields it,
    then deletes the account in teardown regardless of test outcome.

    Yields: dict with 'email' and 'password' keys.
    """
    email = f"siva_managed_{uuid.uuid4().hex[:8]}@mailinator.com"
    payload = new_user_payload(email=email)

    # Setup
    resp = api_client.post(Config.Endpoints.CREATE_ACCOUNT, data=payload)
    body = api_client.parse_response(resp)
    rc = body.get("responseCode") if body else None
    if rc not in (200, 201):
        pytest.skip(
            f"managed_user setup failed (responseCode={rc}). "
            "Check .env credentials or site availability."
        )

    logger.info("managed_user created: %s", email)

    yield {"email": email, "password": payload["password"]}

    # Teardown — best-effort
    api_client.delete(
        Config.Endpoints.DELETE_ACCOUNT,
        data={"email": email, "password": payload["password"]},
    )
    logger.info("managed_user deleted: %s", email)


# ---------------------------------------------------------------------------
# HTML Report Enhancement Hook
# ---------------------------------------------------------------------------

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    Ensures the reports directory exists before tests run.
    """
    import os
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        logger.info("Created reports directory: %s", reports_dir)


def pytest_html_report_title(report):
    """Customize HTML report title."""
    report.title = "Automation Exercise API Test Report"
