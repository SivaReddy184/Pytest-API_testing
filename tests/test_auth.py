"""
tests/test_auth.py
Covers APIs 7 – 10 from AutomationExercise:
  API 7  — POST /verifyLogin valid credentials    → 200, "User exists!"
  API 8  — POST /verifyLogin missing email        → 400, missing param error
  API 9  — DELETE /verifyLogin                   → 405, method not supported
  API 10 — POST /verifyLogin invalid credentials  → 404, "User not found!"
"""

import pytest

from config.config import Config
from data.test_data import VALID_EMAIL, VALID_PASSWORD, INVALID_EMAIL, INVALID_PASSWORD
from utils.api_client import APIClient
from utils.assertions import APIAssertions

ENDPOINT = Config.Endpoints.VERIFY_LOGIN
RC = Config.StatusCode


@pytest.mark.auth
class TestVerifyLoginValid:
    """API 7: POST /verifyLogin with valid email + password."""

    @pytest.mark.smoke
    @pytest.mark.positive
    def test_valid_login_status_200(self, api_client: APIClient, assert_api: APIAssertions):
        """HTTP status must be 200."""
        response = api_client.post(
            ENDPOINT, data={"email": VALID_EMAIL, "password": VALID_PASSWORD}
        )
        assert_api.assert_status_code(response, RC.OK)

    @pytest.mark.positive
    def test_valid_login_body_code_200(self, api_client: APIClient, assert_api: APIAssertions):
        """Body responseCode must be 200."""
        response = api_client.post(
            ENDPOINT, data={"email": VALID_EMAIL, "password": VALID_PASSWORD}
        )
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_response_code_in_body(body, RC.OK)

    @pytest.mark.positive
    def test_valid_login_message(self, api_client: APIClient, assert_api: APIAssertions):
        """Body message must be 'User exists!'."""
        response = api_client.post(
            ENDPOINT, data={"email": VALID_EMAIL, "password": VALID_PASSWORD}
        )
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_message_in_body(body, "User exists!")

    @pytest.mark.positive
    def test_valid_login_response_time(self, api_client: APIClient, assert_api: APIAssertions):
        """Response time must be under 5s."""
        response = api_client.post(
            ENDPOINT, data={"email": VALID_EMAIL, "password": VALID_PASSWORD}
        )
        assert_api.assert_response_time(response, max_seconds=5.0)


@pytest.mark.auth
@pytest.mark.negative
class TestVerifyLoginMissingEmail:
    """API 8: POST /verifyLogin with password only (missing email)."""

    @pytest.mark.smoke
    def test_missing_email_body_code_400(self, api_client: APIClient, assert_api: APIAssertions):
        """Body responseCode must be 400."""
        response = api_client.post(ENDPOINT, data={"password": VALID_PASSWORD})
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_response_code_in_body(body, RC.BAD_REQUEST)

    def test_missing_email_error_message(self, api_client: APIClient, assert_api: APIAssertions):
        """Error message must indicate missing email or password."""
        response = api_client.post(ENDPOINT, data={"password": VALID_PASSWORD})
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_message_in_body(
            body,
            "Bad request, email or password parameter is missing in POST request."
        )

    def test_missing_password_body_code_400(self, api_client: APIClient, assert_api: APIAssertions):
        """Missing password alone should also yield 400."""
        response = api_client.post(ENDPOINT, data={"email": VALID_EMAIL})
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_response_code_in_body(body, RC.BAD_REQUEST)

    def test_missing_both_params_body_code_400(self, api_client: APIClient, assert_api: APIAssertions):
        """Missing both email and password should yield 400."""
        response = api_client.post(ENDPOINT, data={})
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_response_code_in_body(body, RC.BAD_REQUEST)


@pytest.mark.auth
@pytest.mark.negative
class TestVerifyLoginDeleteMethod:
    """API 9: DELETE /verifyLogin — should return 405."""

    @pytest.mark.smoke
    def test_delete_login_body_code_405(self, api_client: APIClient, assert_api: APIAssertions):
        """Body responseCode must be 405."""
        response = api_client.delete(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_response_code_in_body(body, RC.METHOD_NOT_ALLOWED)

    def test_delete_login_error_message(self, api_client: APIClient, assert_api: APIAssertions):
        """Error message must indicate unsupported method."""
        response = api_client.delete(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_message_in_body(body, "This request method is not supported.")


@pytest.mark.auth
@pytest.mark.negative
class TestVerifyLoginInvalidCredentials:
    """API 10: POST /verifyLogin with invalid credentials."""

    @pytest.mark.smoke
    def test_invalid_login_body_code_404(self, api_client: APIClient, assert_api: APIAssertions):
        """Body responseCode must be 404."""
        response = api_client.post(
            ENDPOINT, data={"email": INVALID_EMAIL, "password": INVALID_PASSWORD}
        )
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_response_code_in_body(body, RC.NOT_FOUND)

    def test_invalid_login_message(self, api_client: APIClient, assert_api: APIAssertions):
        """Body message must be 'User not found!'."""
        response = api_client.post(
            ENDPOINT, data={"email": INVALID_EMAIL, "password": INVALID_PASSWORD}
        )
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_message_in_body(body, "User not found!")

    @pytest.mark.parametrize("email,password", [
        (VALID_EMAIL, INVALID_PASSWORD),       # correct email, wrong password
        (INVALID_EMAIL, VALID_PASSWORD),       # wrong email, correct password
        ("", ""),                              # both empty strings
        ("not-an-email", "somepass"),          # malformed email
    ])
    def test_invalid_login_parametrized(
        self, api_client: APIClient, assert_api: APIAssertions, email: str, password: str
    ):
        """All invalid credential combos must result in non-200 responseCode."""
        response = api_client.post(ENDPOINT, data={"email": email, "password": password})
        body = api_client.parse_response(response)
        assert body is not None, "Response body must be parseable."
        rc = body.get("responseCode")
        assert rc != RC.OK, (
            f"Expected non-200 responseCode for email='{email}', got {rc}."
        )
