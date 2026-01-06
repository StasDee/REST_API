# MockAPI Users Management Client

A production-grade Python REST API client designed to demonstrate robust API consumption patterns and clean software design.  
This project was built as **interview-level practice** for REST API automation and backend integration scenarios.

It focuses on correctness, resiliency, readability, and realism rather than shortcuts.

---

## 🎯 Project Goals

- Practice **realistic REST API workflows** (CRUD lifecycle)
- Demonstrate **retry logic**, **timeouts**, and **error handling**
- Use **requests.Session** for efficient HTTP communication
- Implement **clean architecture** with separation of concerns
- Show **production-style logging** and configuration management

---

## 🚀 Key Features

### ✅ Robust Retry Mechanism
- Custom retry decorator with configurable retries and delay
- Retries only on **recoverable failures**:
  - Network errors
  - Timeouts
  - HTTP 5xx responses

### ✅ Session Persistence
- Uses `requests.Session` for:
  - Connection pooling
  - Shared headers
  - Reduced TCP overhead

### ✅ Eventual Consistency Handling
- Verifies deletions by querying remaining resources
- Designed to tolerate delayed backend consistency

### ✅ Environment-Based Configuration
- Secrets and configuration stored in `.env`
- No hard-coded tokens or credentials
- Easy switching between environments

### ✅ Structured, Colorized Logging
- Color-coded output by severity level
- Clear separation between:
  - Application logs
  - HTTP client internals (`urllib3`, `requests`)
- No `print()` usage

### ✅ Deterministic Test Data Generation
- `UserFactory` guarantees **unique users**
- Prevents collisions during repeated test runs
- Suitable for parallel or repeated executions

---

## 🧱 Project Structure

```text
├── .env                # Secret environment variables (API tokens)
├── config.py           # Configuration loader (python-dotenv)
├── decorators.py       # Retry logic with exponential backoff
├── client.py           # UsersApiClient (REST client)
├── factory.py          # UserFactory (unique data generation)
└── main.py             # Scenario orchestration

!!!To run, rename env_example.txt file to .env, you may replace api token with your one!!!

Run from main.py file.
