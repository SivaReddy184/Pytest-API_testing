"""
tests/test_brands.py
Covers API 3 and API 4 from AutomationExercise:
  API 3 — GET /brandsList → 200, returns all brands
  API 4 — PUT /brandsList → 405, method not supported
"""

import pytest

from config.config import Config
from utils.api_client import APIClient
from utils.assertions import APIAssertions

ENDPOINT = Config.Endpoints.BRANDS_LIST
RC = Config.StatusCode


@pytest.mark.brands
class TestGetBrandsList:
    """API 3: GET /brandsList"""

    @pytest.mark.smoke
    @pytest.mark.positive
    def test_get_brands_status_200(self, api_client: APIClient, assert_api: APIAssertions):
        """HTTP status must be 200."""
        response = api_client.get(ENDPOINT)
        assert_api.assert_status_code(response, RC.OK)

    @pytest.mark.positive
    def test_get_brands_response_code_200(self, api_client: APIClient, assert_api: APIAssertions):
        """Body responseCode must be 200."""
        response = api_client.get(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None, "Response body should be parseable JSON."
        assert_api.assert_response_code_in_body(body, RC.OK)

    @pytest.mark.positive
    def test_get_brands_has_brands_key(self, api_client: APIClient, assert_api: APIAssertions):
        """Response body must contain a 'brands' key."""
        response = api_client.get(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_key_exists(body, "brands")

    @pytest.mark.positive
    def test_get_brands_list_not_empty(self, api_client: APIClient, assert_api: APIAssertions):
        """The brands list must not be empty."""
        response = api_client.get(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_list_not_empty(body, "brands")

    @pytest.mark.positive
    def test_get_brands_item_schema(self, api_client: APIClient):
        """Each brand item must contain 'id' and 'brand' fields."""
        response = api_client.get(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None
        brands = body.get("brands", [])
        assert brands, "Brands list is empty."
        first = brands[0]
        required_keys = {"id", "brand"}
        missing = required_keys - set(first.keys())
        assert not missing, f"Brand item missing keys: {missing}. Got: {list(first.keys())}"

    @pytest.mark.positive
    def test_get_brands_response_time(self, api_client: APIClient, assert_api: APIAssertions):
        """Response time should be within 5 seconds."""
        response = api_client.get(ENDPOINT)
        assert_api.assert_response_time(response, max_seconds=5.0)


@pytest.mark.brands
@pytest.mark.negative
class TestPutBrandsList:
    """API 4: PUT /brandsList — should return 405."""

    @pytest.mark.smoke
    def test_put_brands_body_code_405(self, api_client: APIClient, assert_api: APIAssertions):
        """Body responseCode must be 405."""
        response = api_client.put(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_response_code_in_body(body, RC.METHOD_NOT_ALLOWED)

    def test_put_brands_error_message(self, api_client: APIClient, assert_api: APIAssertions):
        """Body message must indicate unsupported method."""
        response = api_client.put(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_message_in_body(body, "This request method is not supported.")
