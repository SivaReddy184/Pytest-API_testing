"""
utils/assertions.py
Reusable assertion helpers that produce clear, descriptive failure messages.
These wrap plain `assert` so pytest's introspection still works but the
error messages are far more readable than raw comparisons.
"""

from typing import Any, Dict, Optional
from requests import Response


class APIAssertions:
    """
    Collection of static assertion methods for API responses.
    Import and call directly — no instantiation needed.
    """

    # ------------------------------------------------------------------
    # Status code
    # ------------------------------------------------------------------

    @staticmethod
    def assert_status_code(response: Response, expected: int) -> None:
        actual = response.status_code
        assert actual == expected, (
            f"[Status Code] Expected {expected}, got {actual}.\n"
            f"URL    : {response.url}\n"
            f"Body   : {response.text[:300]}"
        )

    # ------------------------------------------------------------------
    # Response body — JSON
    # ------------------------------------------------------------------

    @staticmethod
    def assert_response_code_in_body(body: Dict, expected: int) -> None:
        """
        AutomationExercise wraps an inner 'responseCode' key in most responses.
        This asserts that inner code, NOT the HTTP status.
        """
        actual = body.get("responseCode")
        assert actual == expected, (
            f"[Body responseCode] Expected {expected}, got {actual}.\n"
            f"Full body: {body}"
        )

    @staticmethod
    def assert_message_in_body(body: Dict, expected_message: str) -> None:
        actual = body.get("message", "")
        assert actual == expected_message, (
            f"[Body message] Expected '{expected_message}', got '{actual}'.\n"
            f"Full body: {body}"
        )

    @staticmethod
    def assert_message_contains(body: Dict, substring: str) -> None:
        actual = body.get("message", "")
        assert substring.lower() in actual.lower(), (
            f"[Body message] Expected substring '{substring}' not found in '{actual}'.\n"
            f"Full body: {body}"
        )

    @staticmethod
    def assert_key_exists(body: Dict, key: str) -> None:
        assert key in body, (
            f"[Key exists] Expected key '{key}' in response body.\n"
            f"Available keys: {list(body.keys())}"
        )

    @staticmethod
    def assert_list_not_empty(body: Dict, list_key: str) -> None:
        lst = body.get(list_key)
        assert isinstance(lst, list) and len(lst) > 0, (
            f"[List not empty] Expected non-empty list at key '{list_key}'.\n"
            f"Got: {lst}"
        )

    @staticmethod
    def assert_value_equals(body: Dict, key: str, expected: Any) -> None:
        actual = body.get(key)
        assert actual == expected, (
            f"[Value equals] body['{key}'] expected '{expected}', got '{actual}'.\n"
            f"Full body: {body}"
        )

    # ------------------------------------------------------------------
    # Response time
    # ------------------------------------------------------------------

    @staticmethod
    def assert_response_time(response: Response, max_seconds: float = 5.0) -> None:
        elapsed = response.elapsed.total_seconds()
        assert elapsed <= max_seconds, (
            f"[Response Time] Expected <= {max_seconds}s, got {elapsed:.3f}s.\n"
            f"URL: {response.url}"
        )

    # ------------------------------------------------------------------
    # Content-Type
    # ------------------------------------------------------------------

    @staticmethod
    def assert_content_type(response: Response, expected_fragment: str = "application/json") -> None:
        ct = response.headers.get("Content-Type", "")
        assert expected_fragment in ct, (
            f"[Content-Type] Expected '{expected_fragment}' in '{ct}'."
        )
