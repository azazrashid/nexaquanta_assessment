# FastAPI User and Blog Management

This project is a RESTful API built using FastAPI for managing users and blog posts. It includes functionalities for user authentication, CRUD operations for both users and blogs, and caching using Redis to improve performance.

## Key Features

* **User Authentication:** Secure login using email and password.
* **User Management:**
    * Create, read, update, and delete users.
    * Retrieve user details by email.
* **Blog Management:**
    * Create, read, update, and delete blog posts.
    * Authorization to ensure only authors can delete their blogs.
* **Caching:** Utilizes Redis for caching frequently accessed user and blog data to reduce database load.
* **Unit Tests:** Comprehensive unit tests covering authentication, CRUD operations, and caching functionality using Pytest.

## Prerequisites

* **Python 3.12**
* **Poetry** (recommended for dependency management)
* **Docker** 
* **Docker Compose**

## Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd <project_directory>
    ```

2.  **Install dependencies:**

    **Using Poetry (recommended):**
    ```bash
    poetry install
    ```

    **Using pip:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root directory and configure the necessary environment variables, such as database connection details and Redis URL. Example:
    ```env
    DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
    REDIS_URL=redis://localhost:6379/0
    SECRET_KEY=your_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

## Running the Application

This project is configured to run using Docker Compose. Ensure you have Docker and Docker Compose installed on your system.

1.  **Navigate to the root of the project directory in your terminal.**

2.  **Start the application services using Docker Compose:**
    ```bash
    docker compose up --build
    ```
    The `--build` flag ensures that the Docker image for the web service is built if it hasn't been already or if the `Dockerfile` has changed.

    Once the services are up and running, the FastAPI application will be accessible at `http://localhost:8000`. The PostgreSQL database will be accessible on port `5432` on your host machine, and Redis on port `6379`.

3.  **To stop the application, you can run:**
    ```bash
    docker compose down
    ```

## Running the Tests

1.  **Ensure you have `pytest` and `pytest-asyncio` installed:**
    ```bash
    poetry add --dev pytest pytest-asyncio
    # or
    pip install pytest pytest-asyncio
    ```

2.  **Navigate to the root of the project in your terminal.**

3.  **Run the tests using Pytest:**
    ```bash
    pytest
    ```
    This command will discover and run all the tests in the `tests` directory.
