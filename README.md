# MockAPI Users Management Client

A production-grade Python REST API client designed to demonstrate robust API consumption patterns and clean software
design. This project was built as **interview-level practice** for REST API automation and backend integration
scenarios.

It focuses on correctness, resiliency, readability, and realism rather than shortcuts.

---

## Project Goals

- **Practice Realistic Workflows:** Simulate full CRUD (Create, Read, Update, Delete) lifecycles.
- **Resiliency:** Demonstrate professional-grade retry logic, timeouts, and error handling.
- **Efficiency:** Use `requests.Session` for optimized HTTP communication.
- **Clean Architecture:** Maintain a strict separation of concerns between logic, configuration, and data.
- **Observability:** Implement production-style logging instead of basic print statements.

---

## Key Features

### Robust Retry Mechanism

- Custom retry decorator with configurable attempts and exponential backoff.
- Logic specifically targets **recoverable failures**:
    - Network connectivity issues.
    - Request timeouts.
    - HTTP 5xx (Server Error) responses.

### Session Persistence

- Leverages `requests.Session` to provide:
    - **Connection Pooling:** Reuses TCP connections to reduce latency.
    - **Shared Headers:** Consistent Auth and Content-Type management.
    - **Efficiency:** Significant reduction in overhead for high-frequency requests.

### Automatic Resource Cleanup

- Features a **Module-scoped Cleanup Registry** for Pytest.
- Every resource created during a test suite is tracked and verified as deleted during the final teardown, ensuring no
data leakage in the test environment.

### Environment-Based Configuration

- Utilizes `.env` files for secrets and settings.
- Zero hard-coded credentials, allowing for seamless switching between `Staging`, `QA`, and `Production` environments.

### Structured, Colorized Logging

- Professional logging output via the `logging` library.
- **Color-coded severity:** Instantly distinguish between `DEBUG`, `INFO`, and `ERROR`.
- **Filtered Output:** Silences noisy third-party logs (like `urllib3`) to keep terminal output actionable.

### Deterministic Test Data Generation

- Integrated `UserFactory` for generating unique, collision-free user data.
- Ideal for parallel test execution where data isolation is critical.

### Eventual Consistency Handling

- Intelligent verification systems (polling) that confirm resource deletion by re-querying endpoints until a `404` or
  `500` status is confirmed.

---

## Project Structure

```text
.
├── core/                              # Domain logic (backend-style)
│   ├── __init__.py                     # Package initialization
│   ├── normalizers.py                  # Normalize unstable API responses
│   ├── validators.py                   # Business & contract validation logic
│   └── errors.py                       # Domain-specific validation errors
│
├── mockapi_client/                     # Core library package
│   ├── __init__.py                     # Package initialization
│   ├── client.py                        # Main API Client logic & Session handling (sync)
│   ├── async_client.py                  # Async API client using httpx.AsyncClient
│   ├── config.py                        # Pydantic/Dotenv configuration management
│   ├── decorators.py                    # Retry and performance decorators (sync)
│   ├── async_decorators.py              # Async retry and backoff decorators
│   ├── factory.py                       # Test data and User generation logic
│   └── logger.py                        # Logging bridge and formatting
│
├── tests/                               # Automation Suite
│   ├── __init__.py                      # Package initialization
│   ├── conftest.py                       # Shared fixtures (Registry, Client, Factory)
│   ├── test_contract.py                  # Parametrized CRUD/Contract tests (sync)
│   ├── test_scenario.py                  # End-to-End user story scenarios (sync)
│   ├── test_user_contract.py             # Parametrized CRUD/Contract tests (sync)
│   ├── test_user_scenario.py             # End-to-End user story scenarios (sync)
│   ├── test_user_negative.py             # Negative / invalid input tests
│   ├── test_user_async_contract.py       # Async CRUD/Contract tests
│   ├── test_user_async_burst_create.py   # Async burst-load creation test
│   ├── test_user_async_burst_workflow.py # Async burst multi-step workflow test
│   ├── test_user_async_edge_single.py    # Async edge-case single-step tests
│   ├── test_user_async_edge_workflow.py  # Async edge-case workflow tests
│   ├── test_user_concurrent_async_creation.py  # Async parallel creation tests
│   ├── test_user_concurrent_async_conflict.py  # Async conflict/race condition tests
│   └── test_user_concurrency_threads.py        # Legacy threading-based concurrency tests
│
├── __init__.py                           # Package initialization
├── .env                                  # Environment variables (Sensitive)
├── .gitignore                            # Standard Python git exclusions
├── main.py                               # Entry point / Demonstration script
├── pyproject.toml                        # Build system and dependencies
└── README.md                             # Project documentation

```

## Quick Start

Follow these steps to get up and running with the MockAPI Users Management Client.

### 1. Clone the repository

```bash
git clone https://github.com/StasDee/REST_API.git
cd REST_API
```

### 2. Install dependencies

It is recommended to use a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows
```

Then install the package in editable mode:

```bash
pip install -e .
```

Requires Python 3.9 or higher.

### 3. Configure environment

Create a `.env` file in the project root with at least the following variable:

```env
BASE_URL=https://<your_id>.mockapi.io/api/v1/users
TOKEN=your_token_here
```

### 4. Run the main scenario

```bash
python main.py
```

### 5. Execution Modes

#### Option A: Standalone Script

Runs a linear demonstration of the user lifecycle (Create → Fetch → Patch → Delete)

```bash
python main.py
```

#### Option B: Pytest Suite (Recommended)

The project includes a full automation suite with custom markers and module-scoped teardown.
Run all tests from the project root:

```bash
pytest
```

Run specific test categories:

```bash
pytest -m contract   # CRUD lifecycle tests (Parametrized)
pytest -m scenario   # Complex user-story scenarios
```

### 6. Using the API client directly

```python
from mockapi_client.client import UsersApiClient
from mockapi_client.factory import UserFactory

factory = UserFactory()
with UsersApiClient() as api:
    user = factory.create_user_payload()
    created = api.create_user(user)
    print(created)
```
---

## Architecture Overview

This project demonstrates a backend-oriented API test automation architecture, focused on maintainability, scalability, and realistic production patterns.

The design intentionally separates responsibilities into clear layers:

### 1. Client Layer (`mockapi_client`)

Responsible only for HTTP communication and session handling.

- No assertions
- No business logic
- Thin, reusable API wrapper

### 2. Core Layer (`core`)

Contains all reusable logic shared across tests:

- **Normalizers**
  - Convert raw API responses into stable internal representations
  - Handle missing fields, extra fields, and inconsistent formats
- **Validators**
  - Centralized business rules and contract validation
  - Single source of truth for data correctness

This prevents rule duplication and ensures consistent validation across all test types.

### 3. Test Layer (`tests`)

Tests orchestrate behavior rather than reimplement rules.

- **Contract tests**
  - Validate API responses against business rules
  - Focus on data correctness and schema expectations
- **Scenario tests**
  - Model real user workflows (create → fetch → validate)
  - Reuse the same normalization and validation logic

Tests remain thin, readable, and resilient to rule changes.

---

## Design Principles

- **Separation of concerns** – client, core logic, and tests are clearly separated.
- **Single source of truth for validation** – all rules live in one place, tests reuse them.
- **Defensive handling of real-world API inconsistencies** – normalization ensures unstable API responses do not break tests.
- **Backend-style automation** – no UI, no flakiness, focused on API correctness.

This structure mirrors production backend testing patterns rather than tutorial-style test code.

## Test Organization

The `tests/` folder is structured to clearly separate different types of test cases, following **backend-style automation patterns**. This includes classic CRUD tests, negative/edge-case tests, scenario modeling, and new async & concurrency tests.

---

### 1. Positive CRUD / Contract Tests

- **Files:** `test_user_contract.py`, `test_user_async_contract.py`
- **Purpose:** Verify the standard Create → Read → Update → Delete workflows (happy-path scenarios).  
- **Fixtures used:** 
  - `api_client` → provides a reusable synchronous API client.
  - `async_api_client` → provides a reusable async API client.
  - `user_factory` → generates deterministic, valid user payloads.
  - `cleanup_registry` → tracks created users to delete them at module teardown.
- **Markers:** `@pytest.mark.contract`, `@pytest.mark.asyncio` (for async tests).  

### 2. Negative / Edge-Case Tests

- **Files:** `test_user_negative.py`, `test_user_async_edge_single.py`, `test_user_async_edge_workflow.py`
- **Purpose:** Verify that invalid, unexpected, or uncommon user operations are handled correctly by the API client.  
- **Fixtures used:** `api_client` / `async_api_client`, `user_factory`, `cleanup_registry`.
- **Markers:** `@pytest.mark.contract`, `@pytest.mark.edge`, `@pytest.mark.asyncio` (for async tests).

### 3. Scenario / Workflow Tests

- **Files:** `test_scenario.py`, `test_user_scenario.py`, `test_user_async_burst_workflow.py`
- **Purpose:** Model realistic end-to-end user workflows, combining multiple CRUD operations and multi-step async workflows.
- **Markers:** `@pytest.mark.scenario`, `@pytest.mark.asyncio` (for async tests).
- **Design:** Reuses normalization and validation logic from `core/` to keep tests thin and maintainable.

### 4. Async Burst & Concurrency Tests

These tests were added to simulate **high-load and parallel user operations**.

#### 4.1 Async Burst Tests
- **Files:**  
  - `test_user_async_burst_create.py` → Create 20–50 users concurrently (burst load).  
  - `test_user_async_burst_workflow.py` → Multi-step async burst workflow (create → patch → fetch → delete).  
- **Purpose:** Simulate traffic spikes and verify backend stability under load.  
- **Validation:**  
  - All users created successfully.  
  - IDs are unique.  
  - Contract validation passes for all operations.  
- **Markers:** `@pytest.mark.asyncio`, `@pytest.mark.contract`, `@pytest.mark.concurrency` (burst), `@pytest.mark.edge` (multi-step workflow).  

#### 4.2 Async Concurrency / Parallel Tests
- **Files:**  
  - `test_user_concurrent_async_creation.py` → Parallel creation of multiple users.  
  - `test_user_concurrent_async_conflict.py` → Attempt to create multiple users with the **same email simultaneously** (race condition).  
- **Purpose:** Ensure API handles parallel requests and respects unique constraints.  
- **Validation:**  
  - Unique IDs for all users.  
  - Only one user created for duplicate emails.  
  - Exceptions handled gracefully.  
- **Markers:** `@pytest.mark.asyncio`, `@pytest.mark.contract`, `@pytest.mark.concurrency`, `@pytest.mark.edge` (for conflict).  

#### 4.3 Thread-Based Concurrency (Optional)
- **File:** `test_user_concurrency_threads.py`  
- **Purpose:** Legacy threading-based concurrency test for comparison with async execution.  
- **Markers:** `@pytest.mark.contract`, `@pytest.mark.concurrency`.  

---

### 5. Fixtures

- **`api_client`**: Reusable synchronous HTTP client.  
- **`async_api_client`**: Reusable async HTTP client (`httpx.AsyncClient`).  
- **`user_factory`**: Generates unique user data for each test run.  
- **`cleanup_registry`**: Ensures all created users are deleted at teardown to prevent data leakage.  

---

### 6. Markers and Execution Notes

- **Async tests:** `@pytest.mark.asyncio`  
- **Contract tests:** `@pytest.mark.contract`  
- **Concurrency tests:** `@pytest.mark.concurrency`  
- **Edge-case / workflow tests:** `@pytest.mark.edge`  

Async & Concurrency Excecution:

```bash
# Run all async and concurrency tests
pytest -m "async or concurrency" -v -s

# Parallel test execution using pytest-xdist
pytest -m "async or concurrency" -n auto -v -s

# Run only edge workflows
pytest -m "edge" -v -s

# Run only burst creation tests
pytest -m "concurrency and contract" -v -s
```
Best Practices:

Use -v -s for detailed logs.
