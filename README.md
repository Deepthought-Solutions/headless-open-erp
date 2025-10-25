# Headless Open ERP API

[![Run Tests](https://github.com/Deepthought-Solutions/headless-open-erp/actions/workflows/tests.yml/badge.svg)](https://github.com/Deepthought-Solutions/headless-open-erp/actions/workflows/tests.yml)

This directory contains the backend API for the Headless open API application. It is built with Python using the [FastAPI](https://fastapi.tiangolo.com/) framework.

## Architecture

The API follows a classic layered architecture pattern, also known as Clean Architecture or Hexagonal Architecture. This separates the code into distinct layers, each with a specific responsibility. This makes the application more modular, maintainable, and testable.

The main layers are:

*   **Domain Layer (`domain/`)**: This is the core of the application. It contains the business logic and entities.
    *   `orm.py`: Defines the SQLAlchemy ORM models, which represent the database tables.
    *   `contact.py`: Defines the Pydantic models used for data validation and serialization in the API (request and response bodies).

*   **Application Layer (`application/`)**: This layer contains the application-specific business rules. It orchestrates the domain objects to perform use cases.
    *   `*_service.py`: Each service (e.g., `LeadService`, `NoteService`) encapsulates the logic for a specific business domain.

*   **Infrastructure Layer (`infrastructure/`)**: This layer contains all the external concerns, such as the web framework, database access, and third-party integrations.
    *   `web/app.py`: The main FastAPI application file. It defines the API endpoints and handles the HTTP requests and responses.
    *   `database.py`: Configures the database connection using SQLAlchemy.
    *   `mail/sender.py`: A service for sending emails.

## Getting Started

### Prerequisites

*   Python 3.9+
*   A running PostgreSQL database.

### Setup

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Create a `.env` file in this directory (`api/`) and add the following variables. See `.env.example` for a template.
    ```
    DATABASE_URL=postgresql://user:password@host:port/database
    AUTHORIZED_ORIGINS=http://localhost:3000,http://localhost:5173
    MAIL_FROM=...
    MAIL_TO=...
    ALTCHA_HMAC_KEY=...
    OIDC_CLIENT_SECRET=...
    OIDC_ISSUER_URL=...
    ```

### Running the API

To run the API in a local development environment, use the following command:
```bash
uvicorn infrastructure.web.app:app --reload
```
The API will be available at `http://localhost:8000`.

### Running Tests

The tests are located in the `tests/` directory and use `pytest`. To run the tests, execute the following command from the root of the `api` directory:
```bash
pytest
```
The tests run against a separate test database, which is created and destroyed automatically.
