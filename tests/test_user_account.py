"""
tests/test_user_account.py
Covers APIs 11 – 14 from AutomationExercise:
  API 11 — POST /createAccount      → 201, "User created!"
  API 12 — DELETE /deleteAccount    → 200, "Account deleted!"
  API 13 — PUT /updateAccount       → 200, "User updated!"
  API 14 — GET /getUserDetailByEmail → 200, user detail JSON

Important:
  The `managed_user` fixture (conftest.py) handles create + delete lifecycle
  so tests that need a pre-existing user use that fixture instead of
  creating their own — avoiding leftover data.
"""

import uuid
import pytest

from config.config import Config
from data.test_data import new_user_payload, update_user_payload, VALID_EMAIL
from utils.api_client import APIClient
from utils.assertions import APIAssertions

RC = Config.StatusCode


def _fresh_email() -> str:
    return f"siva_fresh_{uuid.uuid4().hex[:8]}@mailinator.com"


# ---------------------------------------------------------------------------
# API 11: Create Account
# ---------------------------------------------------------------------------

@pytest.mark.user
class TestCreateAccount:
    """API 11: POST /createAccount"""

    @pytest.mark.smoke
    @pytest.mark.positive
    def test_create_account_status_201(self, api_client: APIClient, assert_api: APIAssertions):
        """
        Create a new user and assert responseCode == 201.
        Tears down the account immediately after.
        """
        email = _fresh_email()
        payload = new_user_payload(email=email)

        try:
            response = api_client.post(Config.Endpoints.CREATE_ACCOUNT, data=payload)
            body = api_client.parse_response(response)
            assert body is not None, "Response body must be parseable JSON."
            assert_api.assert_response_code_in_body(body, RC.CREATED)
        finally:
            # Teardown — always attempt cleanup
            api_client.delete(
                Config.Endpoints.DELETE_ACCOUNT,
                data={"email": email, "password": payload["password"]},
            )

    @pytest.mark.positive
    def test_create_account_message(self, api_client: APIClient, assert_api: APIAssertions):
        """Body message must be 'User created!'."""
        email = _fresh_email()
        payload = new_user_payload(email=email)

        try:
            response = api_client.post(Config.Endpoints.CREATE_ACCOUNT, data=payload)
            body = api_client.parse_response(response)
            assert body is not None
            assert_api.assert_message_in_body(body, "User created!")
        finally:
            api_client.delete(
                Config.Endpoints.DELETE_ACCOUNT,
                data={"email": email, "password": payload["password"]},
            )

    @pytest.mark.negative
    def test_create_account_duplicate_email(self, api_client: APIClient, managed_user: dict):
        """Creating an account with an already-registered email must not return 201."""
        payload = new_user_payload(email=managed_user["email"])
        payload["password"] = managed_user["password"]

        response = api_client.post(Config.Endpoints.CREATE_ACCOUNT, data=payload)
        body = api_client.parse_response(response)
        assert body is not None
        rc = body.get("responseCode")
        assert rc != RC.CREATED, (
            f"Duplicate account creation should not return 201. Got responseCode={rc}."
        )

    @pytest.mark.negative
    def test_create_account_missing_required_fields(self, api_client: APIClient):
        """Posting without name/email/password must not succeed."""
        response = api_client.post(Config.Endpoints.CREATE_ACCOUNT, data={"title": "Mr"})
        body = api_client.parse_response(response)
        assert body is not None
        rc = body.get("responseCode")
        assert rc != RC.CREATED, (
            f"Incomplete payload should not create a user. Got responseCode={rc}."
        )


# ---------------------------------------------------------------------------
# API 12: Delete Account
# ---------------------------------------------------------------------------

@pytest.mark.user
class TestDeleteAccount:
    """API 12: DELETE /deleteAccount"""

    @pytest.mark.smoke
    @pytest.mark.positive
    def test_delete_account_status_200(self, api_client: APIClient, assert_api: APIAssertions):
        """Create a user, then delete — responseCode must be 200."""
        email = _fresh_email()
        payload = new_user_payload(email=email)

        # Setup
        create_resp = api_client.post(Config.Endpoints.CREATE_ACCOUNT, data=payload)
        create_body = api_client.parse_response(create_resp)
        if not create_body or create_body.get("responseCode") not in (200, 201):
            pytest.skip("Account creation failed — skipping delete test.")

        # Act
        del_resp = api_client.delete(
            Config.Endpoints.DELETE_ACCOUNT,
            data={"email": email, "password": payload["password"]},
        )
        del_body = api_client.parse_response(del_resp)
        assert del_body is not None
        assert_api.assert_response_code_in_body(del_body, RC.OK)

    @pytest.mark.positive
    def test_delete_account_message(self, api_client: APIClient, assert_api: APIAssertions):
        """Body message must be 'Account deleted!'."""
        email = _fresh_email()
        payload = new_user_payload(email=email)

        api_client.post(Config.Endpoints.CREATE_ACCOUNT, data=payload)
        del_resp = api_client.delete(
            Config.Endpoints.DELETE_ACCOUNT,
            data={"email": email, "password": payload["password"]},
        )
        del_body = api_client.parse_response(del_resp)
        assert del_body is not None
        assert_api.assert_message_in_body(del_body, "Account deleted!")

    @pytest.mark.negative
    def test_delete_nonexistent_account(self, api_client: APIClient):
        """Deleting a non-existent account must not return 200."""
        del_resp = api_client.delete(
            Config.Endpoints.DELETE_ACCOUNT,
            data={"email": "ghost_nobody@mailinator.com", "password": "WrongPass1!"},
        )
        body = api_client.parse_response(del_resp)
        assert body is not None
        rc = body.get("responseCode")
        assert rc != RC.OK, f"Expected non-200 for non-existent account, got {rc}."


# ---------------------------------------------------------------------------
# API 13: Update Account
# ---------------------------------------------------------------------------

@pytest.mark.user
class TestUpdateAccount:
    """API 13: PUT /updateAccount"""

    @pytest.mark.smoke
    @pytest.mark.positive
    def test_update_account_status_200(self, api_client: APIClient, assert_api: APIAssertions, managed_user: dict):
        """Update managed user — responseCode must be 200."""
        payload = update_user_payload(email=managed_user["email"])
        payload["password"] = managed_user["password"]

        response = api_client.put(Config.Endpoints.UPDATE_ACCOUNT, data=payload)
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_response_code_in_body(body, RC.OK)

    @pytest.mark.positive
    def test_update_account_message(self, api_client: APIClient, assert_api: APIAssertions, managed_user: dict):
        """Body message must be 'User updated!'."""
        payload = update_user_payload(email=managed_user["email"])
        payload["password"] = managed_user["password"]

        response = api_client.put(Config.Endpoints.UPDATE_ACCOUNT, data=payload)
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_message_in_body(body, "User updated!")

    @pytest.mark.negative
    def test_update_nonexistent_account(self, api_client: APIClient):
        """Updating a non-existent account must not return 200."""
        payload = update_user_payload(email="ghost_nobody@mailinator.com")
        payload["password"] = "WrongPass1!"

        response = api_client.put(Config.Endpoints.UPDATE_ACCOUNT, data=payload)
        body = api_client.parse_response(response)
        assert body is not None
        rc = body.get("responseCode")
        assert rc != RC.OK, f"Expected non-200 for non-existent account, got {rc}."


# ---------------------------------------------------------------------------
# API 14: Get User Detail By Email
# ---------------------------------------------------------------------------

@pytest.mark.user
class TestGetUserDetailByEmail:
    """API 14: GET /getUserDetailByEmail"""

    @pytest.mark.smoke
    @pytest.mark.positive
    def test_get_user_detail_status_200(self, api_client: APIClient, assert_api: APIAssertions, managed_user: dict):
        """Fetching detail of managed user — HTTP status must be 200."""
        response = api_client.get(
            Config.Endpoints.GET_USER_DETAIL,
            params={"email": managed_user["email"]},
        )
        assert_api.assert_status_code(response, RC.OK)

    @pytest.mark.positive
    def test_get_user_detail_body_code_200(self, api_client: APIClient, assert_api: APIAssertions, managed_user: dict):
        """Body responseCode must be 200."""
        response = api_client.get(
            Config.Endpoints.GET_USER_DETAIL,
            params={"email": managed_user["email"]},
        )
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_response_code_in_body(body, RC.OK)

    @pytest.mark.positive
    def test_get_user_detail_has_user_key(self, api_client: APIClient, assert_api: APIAssertions, managed_user: dict):
        """Response body must contain a 'user' key."""
        response = api_client.get(
            Config.Endpoints.GET_USER_DETAIL,
            params={"email": managed_user["email"]},
        )
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_key_exists(body, "user")

    @pytest.mark.positive
    def test_get_user_detail_email_matches(self, api_client: APIClient, managed_user: dict):
        """The email in the response must match the requested email."""
        response = api_client.get(
            Config.Endpoints.GET_USER_DETAIL,
            params={"email": managed_user["email"]},
        )
        body = api_client.parse_response(response)
        assert body is not None
        user = body.get("user", {})
        assert user.get("email") == managed_user["email"], (
            f"Expected email '{managed_user['email']}', got '{user.get('email')}'."
        )

    @pytest.mark.positive
    def test_get_user_detail_schema(self, api_client: APIClient, managed_user: dict):
        """User object must contain standard fields."""
        response = api_client.get(
            Config.Endpoints.GET_USER_DETAIL,
            params={"email": managed_user["email"]},
        )
        body = api_client.parse_response(response)
        assert body is not None
        user = body.get("user", {})
        required_keys = {"id", "name", "email"}
        missing = required_keys - set(user.keys())
        assert not missing, f"User detail missing keys: {missing}. Got: {list(user.keys())}"

    @pytest.mark.negative
    def test_get_user_detail_missing_email_param(self, api_client: APIClient):
        """Omitting email param should not return 200."""
        response = api_client.get(Config.Endpoints.GET_USER_DETAIL)
        body = api_client.parse_response(response)
        assert body is not None
        rc = body.get("responseCode")
        assert rc != RC.OK, f"Expected non-200 when email param missing, got {rc}."

    @pytest.mark.negative
    def test_get_user_detail_nonexistent_email(self, api_client: APIClient):
        """Non-existent email must not return 200."""
        response = api_client.get(
            Config.Endpoints.GET_USER_DETAIL,
            params={"email": "nobody_xyz_12345@mailinator.com"},
        )
        body = api_client.parse_response(response)
        assert body is not None
        rc = body.get("responseCode")
        assert rc != RC.OK, f"Expected non-200 for unknown email, got {rc}."

    @pytest.mark.positive
    def test_get_user_detail_response_time(self, api_client: APIClient, assert_api: APIAssertions, managed_user: dict):
        """Response time must be within 5s."""
        response = api_client.get(
            Config.Endpoints.GET_USER_DETAIL,
            params={"email": managed_user["email"]},
        )
        assert_api.assert_response_time(response, max_seconds=5.0)
