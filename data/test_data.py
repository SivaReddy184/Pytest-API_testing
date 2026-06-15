"""
data/test_data.py
Static test-data constants used across the test suite.
Keep all hardcoded values here so tests stay readable.
"""

import uuid


def _unique_email() -> str:
    """Generate a unique email address to avoid collisions between runs."""
    return f"siva_test_{uuid.uuid4().hex[:8]}@mailinator.com"


# ---- Auth ---------------------------------------------------------------

VALID_EMAIL = "testuser_siva@example.com"   # Must exist on the site
VALID_PASSWORD = "Test@1234"

INVALID_EMAIL = "nonexistent_xyz@nowhere.com"
INVALID_PASSWORD = "WrongPass999"

# ---- Search -------------------------------------------------------------

SEARCH_TERMS = {
    "top": "top",
    "tshirt": "tshirt",
    "jean": "jean",
}

# ---- New user payload ---------------------------------------------------
# A fresh email is generated each test run so create/delete don't conflict.

def new_user_payload(email: str = None) -> dict:
    email = email or _unique_email()
    return {
        "name": "Siva Test",
        "email": email,
        "password": "AutoTest@123",
        "title": "Mr",
        "birth_date": "10",
        "birth_month": "6",
        "birth_year": "1995",
        "firstname": "Siva",
        "lastname": "QA",
        "company": "Evernorth",
        "address1": "123 Test Street",
        "address2": "Suite 4B",
        "country": "India",
        "zipcode": "500001",
        "state": "Telangana",
        "city": "Hyderabad",
        "mobile_number": "9876543210",
    }


# ---- Update user payload ------------------------------------------------

def update_user_payload(email: str) -> dict:
    payload = new_user_payload(email)
    payload["name"] = "Siva Updated"
    payload["city"] = "Vijayawada"
    return payload
