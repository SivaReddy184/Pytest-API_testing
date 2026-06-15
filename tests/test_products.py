"""
tests/test_products.py
Covers API 1 and API 2 from AutomationExercise:
  API 1 — GET /productsList  → 200, returns all products
  API 2 — POST /productsList → 405, method not supported
"""

import pytest

from config.config import Config
from utils.api_client import APIClient
from utils.assertions import APIAssertions

ENDPOINT = Config.Endpoints.PRODUCTS_LIST
RC = Config.StatusCode


@pytest.mark.products
class TestGetProductsList:
    """API 1: GET /productsList"""

    @pytest.mark.smoke
    @pytest.mark.positive
    def test_get_products_status_200(self, api_client: APIClient, assert_api: APIAssertions):
        """HTTP status must be 200."""
        response = api_client.get(ENDPOINT)
        assert_api.assert_status_code(response, RC.OK)

    @pytest.mark.positive
    def test_get_products_response_code_200(self, api_client: APIClient, assert_api: APIAssertions):
        """Body responseCode must also be 200."""
        response = api_client.get(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None, "Response body should be parseable JSON."
        assert_api.assert_response_code_in_body(body, RC.OK)

    @pytest.mark.positive
    def test_get_products_has_products_key(self, api_client: APIClient, assert_api: APIAssertions):
        """Response body must contain a 'products' key."""
        response = api_client.get(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_key_exists(body, "products")

    @pytest.mark.positive
    def test_get_products_list_not_empty(self, api_client: APIClient, assert_api: APIAssertions):
        """The products list must not be empty."""
        response = api_client.get(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_list_not_empty(body, "products")

    @pytest.mark.positive
    def test_get_products_item_schema(self, api_client: APIClient):
        """Each product item must contain expected fields."""
        response = api_client.get(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None
        products = body.get("products", [])
        assert products, "Products list is empty."
        first = products[0]
        required_keys = {"id", "name", "price", "brand", "category"}
        missing = required_keys - set(first.keys())
        assert not missing, f"Product item missing keys: {missing}. Got: {list(first.keys())}"

    @pytest.mark.positive
    def test_get_products_response_time(self, api_client: APIClient, assert_api: APIAssertions):
        """Response time should be within 5 seconds."""
        response = api_client.get(ENDPOINT)
        assert_api.assert_response_time(response, max_seconds=5.0)


@pytest.mark.products
@pytest.mark.negative
class TestPostProductsList:
    """API 2: POST /productsList — should return 405."""

    @pytest.mark.smoke
    def test_post_products_status_405(self, api_client: APIClient, assert_api: APIAssertions):
        """HTTP status must be 200 (the site wraps 405 in a 200 envelope)."""
        response = api_client.post(ENDPOINT)
        # AutomationExercise returns HTTP 200 but wraps the 405 in the body
        assert_api.assert_status_code(response, RC.OK)

    def test_post_products_body_code_405(self, api_client: APIClient, assert_api: APIAssertions):
        """Body responseCode must be 405."""
        response = api_client.post(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_response_code_in_body(body, RC.METHOD_NOT_ALLOWED)

    def test_post_products_error_message(self, api_client: APIClient, assert_api: APIAssertions):
        """Body message must indicate unsupported method."""
        response = api_client.post(ENDPOINT)
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_message_in_body(body, "This request method is not supported.")
