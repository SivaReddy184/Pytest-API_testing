"""
utils/api_client.py
A thin, opinionated wrapper around requests.Session that provides:
  - A single session reused across all calls (connection pooling)
  - Automatic base-URL prefixing
  - Consistent timeout enforcement
  - Structured request/response logging
  - JSON response parsing with graceful fallback
"""

import json
import logging
from typing import Any, Dict, Optional

import requests
from requests import Response

from config.config import Config

logger = logging.getLogger(__name__)


class APIClient:
    """Thin wrapper around requests.Session with base-URL, timeout, and logging."""

    def __init__(
        self,
        base_url: str = Config.BASE_URL,
        timeout: int = Config.REQUEST_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(Config.DEFAULT_HEADERS)
        if headers:
            self.session.headers.update(headers)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def _log_request(self, method: str, url: str, **kwargs: Any) -> None:
        logger.info(">>> %s %s", method.upper(), url)
        if kwargs.get("params"):
            logger.debug("    params : %s", kwargs["params"])
        if kwargs.get("data"):
            logger.debug("    data   : %s", kwargs["data"])
        if kwargs.get("json"):
            logger.debug("    json   : %s", kwargs["json"])

    def _log_response(self, response: Response) -> None:
        logger.info(
            "<<< %s %s  [%dms]",
            response.status_code,
            response.reason,
            int(response.elapsed.total_seconds() * 1000),
        )
        try:
            logger.debug("    body   : %s", response.json())
        except ValueError:
            logger.debug("    body   : %s", response.text[:200])

    def _parse_json(self, response: Response) -> Optional[Dict]:
        """
        AutomationExercise wraps its JSON inside a string sometimes.
        This handles both a proper JSON body and a plain-text body.
        """
        try:
            return response.json()
        except ValueError:
            # Some endpoints return a JSON-like string without content-type
            try:
                return json.loads(response.text)
            except (ValueError, TypeError):
                return None

    # ------------------------------------------------------------------
    # Public HTTP verbs
    # ------------------------------------------------------------------

    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Response:
        url = self._url(endpoint)
        self._log_request("GET", url, params=params)
        response = self.session.get(url, params=params, timeout=self.timeout, **kwargs)
        self._log_response(response)
        return response

    def post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        json_body: Optional[Dict] = None,
        **kwargs,
    ) -> Response:
        url = self._url(endpoint)
        self._log_request("POST", url, data=data, json=json_body)
        response = self.session.post(
            url, data=data, json=json_body, timeout=self.timeout, **kwargs
        )
        self._log_response(response)
        return response

    def put(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        json_body: Optional[Dict] = None,
        **kwargs,
    ) -> Response:
        url = self._url(endpoint)
        self._log_request("PUT", url, data=data, json=json_body)
        response = self.session.put(
            url, data=data, json=json_body, timeout=self.timeout, **kwargs
        )
        self._log_response(response)
        return response

    def delete(
        self, endpoint: str, data: Optional[Dict] = None, **kwargs
    ) -> Response:
        url = self._url(endpoint)
        self._log_request("DELETE", url, data=data)
        response = self.session.delete(
            url, data=data, timeout=self.timeout, **kwargs
        )
        self._log_response(response)
        return response

    def parse_response(self, response: Response) -> Optional[Dict]:
        """Public proxy to _parse_json — used in test assertions."""
        return self._parse_json(response)

    def close(self) -> None:
        self.session.close()
