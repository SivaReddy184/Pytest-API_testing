"""
tests/test_search.py
Covers API 5 and API 6 from AutomationExercise:
  API 5 — POST /searchProduct with valid param  → 200, returns matched products
  API 6 — POST /searchProduct without param     → 400, missing parameter error
"""

import pytest

from config.config import Config
from data.test_data import SEARCH_TERMS
from utils.api_client import APIClient
from utils.assertions import APIAssertions

ENDPOINT = Config.Endpoints.SEARCH_PRODUCT
RC = Config.StatusCode


@pytest.mark.search
class TestSearchProduct:
    """API 5: POST /searchProduct with valid search_product parameter."""

    @pytest.mark.smoke
    @pytest.mark.positive
    def test_search_top_status_200(self, api_client: APIClient, assert_api: APIAssertions):
        """Search for 'top' — HTTP status must be 200."""
        response = api_client.post(ENDPOINT, data={"search_product": SEARCH_TERMS["top"]})
        assert_api.assert_status_code(response, RC.OK)

    @pytest.mark.positive
    def test_search_top_response_code_200(self, api_client: APIClient, assert_api: APIAssertions):
        """Search for 'top' — body responseCode must be 200."""
        response = api_client.post(ENDPOINT, data={"search_product": SEARCH_TERMS["top"]})
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_response_code_in_body(body, RC.OK)

    @pytest.mark.positive
    def test_search_top_has_products(self, api_client: APIClient, assert_api: APIAssertions):
        """Searching 'top' must return a non-empty products list."""
        response = api_client.post(ENDPOINT, data={"search_product": SEARCH_TERMS["top"]})
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_key_exists(body, "products")
        assert_api.assert_list_not_empty(body, "products")

    @pytest.mark.positive
    @pytest.mark.parametrize("term", list(SEARCH_TERMS.values()))
    def test_search_parametrized(self, api_client: APIClient, assert_api: APIAssertions, term: str):
        """Parametrized: each known search term must return 200 and a products list."""
        response = api_client.post(ENDPOINT, data={"search_product": term})
        body = api_client.parse_response(response)
        assert body is not None, f"No parseable body for term='{term}'"
        assert_api.assert_response_code_in_body(body, RC.OK)
        assert_api.assert_key_exists(body, "products")

    @pytest.mark.positive
    def test_search_result_item_schema(self, api_client: APIClient):
        """Each item in search results must have expected fields."""
        response = api_client.post(ENDPOINT, data={"search_product": "tshirt"})
        body = api_client.parse_response(response)
        assert body is not None
        products = body.get("products", [])
        if products:
            first = products[0]
            for key in ("id", "name", "price"):
                assert key in first, f"Expected key '{key}' not found in search result item."


@pytest.mark.search
@pytest.mark.negative
class TestSearchProductMissingParam:
    """API 6: POST /searchProduct without search_product parameter."""

    @pytest.mark.smoke
    def test_search_no_param_body_code_400(self, api_client: APIClient, assert_api: APIAssertions):
        """Body responseCode must be 400 when parameter is missing."""
        response = api_client.post(ENDPOINT, data={})
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_response_code_in_body(body, RC.BAD_REQUEST)

    def test_search_no_param_error_message(self, api_client: APIClient, assert_api: APIAssertions):
        """Error message must mention missing search_product parameter."""
        response = api_client.post(ENDPOINT, data={})
        body = api_client.parse_response(response)
        assert body is not None
        assert_api.assert_message_in_body(
            body,
            "Bad request, search_product parameter is missing in POST request."
        )

    def test_search_empty_string_param(self, api_client: APIClient):
        """Edge case: empty string value for search_product should still get a response."""
        response = api_client.post(ENDPOINT, data={"search_product": ""})
        assert response is not None
        # Site may return 200 with empty list or 400 — either is acceptable
        assert response.status_code in (RC.OK, RC.BAD_REQUEST), (
            f"Unexpected status {response.status_code} for empty search_product."
        )
