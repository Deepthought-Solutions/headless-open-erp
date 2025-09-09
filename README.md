# Headless API

This directory contains the backend API for the Headless application. It is built with Rust using the [Axum](https://github.com/tokio-rs/axum) framework.

DATABASE_URL

cargo install sqlx-cli

The main layers are:

*   **Domain Layer (`src/domain/`)**: This is the core of the application. It contains the business logic and entities.
*   **Application Layer (`src/application/`)**: This layer contains the application-specific business rules. It orchestrates the domain objects to perform use cases.
*   **Infrastructure Layer (`src/infrastructure/`)**: This layer contains all the external concerns, such as the web framework, database access, and third-party integrations.

## Getting Started

This guide will help you get the application running on your local machine.

### Prerequisites

*   [Rust](https://www.rust-lang.org/tools/install) (latest stable version)
*   [Cargo](https://doc.rust-lang.org/cargo/) (comes with Rust)
*   [PostgreSQL](https://www.postgresql.org/download/)
*   [Docker](https://docs.docker.com/get-docker/) (for containerized setup)
*   [refinery_cli](https://crates.io/crates/refinery_cli)

You can install `refinery_cli` with the following command:
```bash
cargo install refinery_cli
```

### Running Locally

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd headless-api
    ```

2.  **Set up the database:**
    Make sure you have a PostgreSQL instance running. Create a database for the application.

3.  **Configure environment variables:**
    Create a `.env` file in the root of the project and add the following variable.
    ```
    DATABASE_URL=postgres://user:password@host:port/database
    ```
    Replace `user`, `password`, `host`, `port`, and `database` with your PostgreSQL connection details. For example:
    ```
    DATABASE_URL=postgres://postgres:postgres@127.0.0.1:5432/main
    ```

4.  **Run database migrations:**
    ```bash
    refinery migrate -c refinery.toml -p .
    ```

5.  **Build and run the application:**
    ```bash
    cargo run
    ```
    The API will be available at `http://localhost:8000`.

### Running with Docker

You can also run the application using Docker and Docker Compose. A `docker-compose.yml` file is provided for convenience.

1.  **Start the services:**
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker image for the application, start a PostgreSQL container, run the database migrations, and start the API.

2.  **Access the API:**
    The API will be available at `http://localhost:8000`.

3.  **Stopping the services:**
    To stop the containers, press `Ctrl+C` in the terminal where `docker-compose` is running, or run the following command from another terminal:
    ```bash
    docker-compose down
    ```
