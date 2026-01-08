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
- Every resource created during a test suite is tracked and verified as deleted during the final teardown, ensuring no "
  data leaking" in the test environment.

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

### 🔍 Eventual Consistency Handling

- Intelligent verification systems (polling) that confirm resource deletion by re-querying endpoints until a `404` or
  `500` status is confirmed.

---

## Project Structure

```text
.
├── mockapi_client/           # Core library package
│   ├── __init__.py           # Package initialization
│   ├── client.py             # Main API Client logic & Session handling
│   ├── config.py             # Pydantic/Dotenv configuration management
│   ├── decorators.py         # Retry and performance decorators
│   ├── factory.py            # Test data and User generation logic
│   └── logger.py             # Logging bridge and formatting
├── tests/                    # Automation Suite
│   ├── __init__.py           # Package initialization
│   ├── conftest.py           # Shared fixtures (Registry, Client, Factory)
│   ├── test_contract.py      # Parametrized CRUD/Contract tests
│   └── test_scenario.py      # End-to-End user story scenarios
├── __init__.py               # Package initialization
├── .env                      # Environment variables (Sensitive)
├── .gitignore                # Standard Python git exclusions
├── main.py                   # Entry point / Demonstration script
├── pyproject.toml            # Build system and dependencies
└── README.md                 # Project documentation
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

Runs from withing a project a linear demonstration of the user lifecycle (Create → Fetch → Patch → Delete)

```bash
python main.py
```

#### Option B: Pytest Suite (Recommended)

The project includes a full automation suite with custom markers and module-scoped teardown.
Run from withing a project all tests:

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
