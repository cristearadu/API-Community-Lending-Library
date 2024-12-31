# API Community Lending Library

A RESTful API for managing a community lending library system.

## Prerequisites

- **Docker Desktop**
- **Git**

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/API-Community-Lending-Library.git
cd API-Community-Lending-Library
```

### 2. Start Docker Desktop

- Ensure Docker Desktop is running on your machine.
- [Download Docker Desktop](https://www.docker.com/products/docker-desktop/) if it is not installed.

### 3. Run Setup

Choose the appropriate method based on your operating system:

#### Unix/MacOS
```bash
./setup.sh
```

#### Windows (PowerShell)
```powershell
.\setup.ps1
```

#### Windows (Command Prompt)
```batch
setup.bat
```

The setup script will:
- Build the Docker containers.
- Start the application.
- Run all tests.
- Show live logs (press `Ctrl+C` to exit logs).

## Accessing the API

Once running, you can access:

- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Default Admin Credentials

- **Username:** `admin`
- **Password:** `Admin123!`
- **Email:** `admin@example.com`

## Manual Docker Commands

If needed, you can manage Docker manually using the following commands:

### Build Containers
```bash
docker compose build
```

### Start Containers
```bash
docker compose up -d
```

### View Logs
```bash
docker compose logs -f
```

### Stop Containers
```bash
docker compose down
```

## Project Structure

```
├── alembic/              # Database migrations
├── models/               # SQLAlchemy models
├── routers/              # API routes
├── schemas/              # Pydantic models
├── services/             # Business logic
├── tests/                # Test files
├── uploads/              # File uploads directory
├── docker-compose.yml    # Docker configuration
├── Dockerfile            # Docker build instructions
└── requirements.txt      # Python dependencies
```

---
