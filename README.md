# AutomationExercise API Testing Framework

A robust, industry-standard API test automation framework built with **Python + pytest + requests**, covering all 14 REST APIs from [AutomationExercise](https://automationexercise.com/api_list).

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| `Python 3.9+` | Language |
| `requests` | HTTP client |
| `pytest` | Test runner and assertion engine |
| `pytest-html` | Auto-generated HTML reports |
| `pytest-xdist` | Parallel test execution |
| `python-dotenv` | Environment variable management |
| `faker` | Dynamic test data generation |

---

## Project Structure

```
automationexercise_api_framework/
│
├── config/
│   ├── __init__.py
│   └── config.py             # Centralised Config class (URLs, status codes, headers)
│
├── data/
│   ├── __init__.py
│   └── test_data.py          # All static test data and payload builders
│
├── utils/
│   ├── __init__.py
│   ├── api_client.py         # requests.Session wrapper with logging
│   └── assertions.py         # Reusable assertion helpers
│
├── tests/
│   ├── __init__.py
│   ├── test_products.py      # API 1, 2  — Products
│   ├── test_brands.py        # API 3, 4  — Brands
│   ├── test_search.py        # API 5, 6  — Search
│   ├── test_auth.py          # API 7–10  — Login / Auth
│   └── test_user_account.py  # API 11–14 — User CRUD
│
├── reports/                  # Auto-generated HTML reports land here
├── conftest.py               # Shared fixtures (api_client, managed_user, assert_api)
├── pytest.ini                # Markers, logging, default addopts
├── requirements.txt
├── Makefile
├── .env                      # Local secrets — never commit this
└── .gitignore
```

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd automationexercise_api_framework

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
# or
make install
```

### 3. Configure credentials

Edit `.env` with a valid registered account from AutomationExercise:

```env
BASE_URL=https://automationexercise.com/api
VALID_EMAIL=your_registered_email@example.com
VALID_PASSWORD=YourPassword123
REQUEST_TIMEOUT=30
```

> **Note:** `VALID_EMAIL` / `VALID_PASSWORD` must be a real account on the site for login tests (API 7, 10) to pass. Register one at https://automationexercise.com/signup.

---

## Running Tests

### Quick reference

```bash
# Full regression suite
pytest

# Or via Makefile
make regression
```

### By marker (selective runs)

```bash
# Smoke tests only — fastest sanity check
make smoke
# equivalent: pytest -m smoke -v

# By domain
make products    # API 1, 2
make brands      # API 3, 4
make search      # API 5, 6
make auth        # API 7, 8, 9, 10
make user        # API 11, 12, 13, 14

# By test type
make positive
make negative

# Parallel execution
make parallel    # pytest -n auto
```

### Dry run — list tests without executing

```bash
make collect
# equivalent: pytest --collect-only -q
```

---

## HTML Report

A self-contained HTML report is auto-generated after every run:

```
reports/report.html
```

Open it in any browser — no server needed. It includes pass/fail status, test durations, and captured log output per test.

---

## API Coverage

| API | Endpoint | Method | Tests |
|-----|----------|--------|-------|
| 1 | `/productsList` | GET | Status 200, body schema, list not empty, response time |
| 2 | `/productsList` | POST | Body code 405, error message |
| 3 | `/brandsList` | GET | Status 200, body schema, list not empty, response time |
| 4 | `/brandsList` | PUT | Body code 405, error message |
| 5 | `/searchProduct` | POST (with param) | Status 200, results returned, schema, parametrized terms |
| 6 | `/searchProduct` | POST (no param) | Body code 400, error message, empty string edge case |
| 7 | `/verifyLogin` | POST (valid) | Status 200, "User exists!", response time |
| 8 | `/verifyLogin` | POST (missing email) | Body code 400, missing both, missing password |
| 9 | `/verifyLogin` | DELETE | Body code 405, error message |
| 10 | `/verifyLogin` | POST (invalid) | Body code 404, "User not found!", parametrized combos |
| 11 | `/createAccount` | POST | Body code 201, "User created!", duplicate email, missing fields |
| 12 | `/deleteAccount` | DELETE | Body code 200, "Account deleted!", non-existent account |
| 13 | `/updateAccount` | PUT | Body code 200, "User updated!", non-existent account |
| 14 | `/getUserDetailByEmail` | GET | Status 200, user schema, email match, missing param, unknown email |

**Total: 40+ test cases across 14 APIs.**

---

## Key Design Decisions

### `requests.Session` for connection pooling
All HTTP calls share one `requests.Session` instance (session-scoped fixture) — faster test runs through TCP connection reuse.

### `managed_user` fixture for safe CRUD lifecycle
Tests that need a real user account use the `managed_user` fixture which creates a fresh account in setup and deletes it in teardown — regardless of whether the test passes or fails. No leftover test data.

### Separate body `responseCode` vs HTTP status
AutomationExercise wraps its own response code inside the JSON body (`{"responseCode": 405, ...}`). `APIAssertions` has dedicated methods for both the HTTP status and the inner body code — they are asserted independently and intentionally.

### All test data centralised in `data/test_data.py`
No magic strings inside test files. All payloads, credentials, and search terms live in one place.

---

## Markers Reference

```
smoke       — Quick sanity: one happy-path test per endpoint
regression  — (default) Full suite
products    — API 1-2
brands      — API 3-4
search      — API 5-6
auth        — API 7-10
user        — API 11-14
positive    — Happy-path tests
negative    — Error/edge-case tests
```

---

## Cleanup

```bash
make clean
```

Removes `__pycache__`, `.pytest_cache`, and the `reports/` HTML file.
