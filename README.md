# MockAPI Users Management Client

A robust, production-grade Python REST API client designed to interact with MockAPI. This project demonstrates advanced concepts in API consumption, including exponential backoff retries, session management, and eventual consistency handling.

!!!To run, rename env_example.txt file to .env, you may replace api token with your one!!!

## 🚀 Features

- **Robust Retry Mechanism**: Custom decorator using exponential backoff to handle 500-series errors and network timeouts.
- **Session Persistence**: Utilizes `requests.Session` for connection pooling and automatic header management.
- **Eventual Consistency Handling**: Implements a polling verification loop to handle delayed API deletions.
- **Environment Configuration**: Decouples secrets and configuration using `.env` files.
- **Colorized Logging**: Detailed, color-coded terminal output for better debugging and observability.
- **Unique Data Generation**: A `UserFactory` that ensures 100% unique data during test runs using a set-based collision check.

## 🛠 Project Structure

```text
├── .env                # Secret environment variables (API tokens)
├── config.py           # Configuration loader using python-dotenv
├── decorators.py       # Retry logic with exponential backoff
├── client.py           # Core UsersApiClient implementation
├── factory.py          # Unique user data generation logic
└── main.py             # Orchestration and scenario execution
