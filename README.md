# API Community Lending Library

A RESTful API for managing a community lending library system.

## Prerequisites

- Python 3.10 or higher
- Docker Desktop
- Git

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/API-Community-Lending-Library.git
   cd API-Community-Lending-Library
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   
   # For Windows
   .\.venv\Scripts\activate
   
   # For macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

1. **Start Docker Desktop**
   - Make sure Docker Desktop is running on your machine
   - You can download it from [Docker's official website](https://www.docker.com/products/docker-desktop/) if not installed

2. **Start the API and Run Tests**
   ```bash
   python setup.py
   ```
   This will:
   - Start the API in a Docker container
   - Check if the API is healthy
   - Run all tests
   - Keep the container running if tests pass

3. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Documentation: http://localhost:8000/redoc

## Testing

The API will be running at `http://localhost:8000`. You can:
- Use the Swagger UI for manual testing
- Write automated tests using your preferred testing framework
- Use tools like Postman or curl for API requests

## Stopping the API

When you're done testing, stop the Docker container: