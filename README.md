# Wedding Backend API

A robust, production-ready FastAPI backend service for managing wedding organizations with multi-tenant architecture, authentication, and comprehensive testing.

## Features

- 🏢 **Multi-tenant Organization Management** - Create, update, and manage organizations
- 🔐 **JWT-based Authentication** - Secure admin authentication with JWT tokens
- 🗄️ **MongoDB Integration** - Scalable database with tenant isolation
- ✅ **Comprehensive Validation** - Input validation using Pydantic
- 🧪 **Full Test Coverage** - Unit, integration, and API tests
- 🐳 **Docker Support** - Containerized deployment
- 🔒 **Security** - Password hashing with bcrypt, security scanning
- 📊 **Code Quality** - Linting, formatting, type checking

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB 6.0
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Validation**: Pydantic v2
- **Testing**: pytest, pytest-cov
- **Code Quality**: ruff, black, mypy, bandit

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- MongoDB (or use Docker)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd wedding-backend
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Or run locally**
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Organization Management

- `POST /org/create` - Create a new organization
- `GET /org/get?organization_name={name}` - Get organization details
- `PUT /org/update?current_name={old}&new_name={new}` - Update organization (requires auth)
- `DELETE /org/delete?org_name={name}` - Delete organization (requires auth)
<img width="1004" height="731" alt="Wedding Company Backend APIs" src="https://github.com/user-attachments/assets/db6903c4-7664-4f1d-9720-b005d79a484c" />

### Authentication

- `POST /admin/login` - Admin login (returns JWT token)

### Health Check

- `GET /` - Health check endpoint

## Development

### Setup Development Environment

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_org_endpoints.py
```

### Code Quality

```bash
# Format code
black app/ scripts/

# Lint code
ruff check app/ scripts/

# Type check
mypy app/

# Security scan
bandit -r app/
```

### Using Makefile

```bash
# Install dependencies
make install

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Security scan
make security

# Run all quality checks
make quality

# Start services
make up

# Stop services
make down

# Rebuild containers
make rebuild
```

## Project Structure

```
wedding-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # MongoDB connection
│   ├── dependencies.py     # FastAPI dependencies
│   ├── schemas.py           # Pydantic models
│   ├── routes/              # API routes
│   │   ├── auth.py
│   │   └── org.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   └── org_service.py
│   ├── utils/               # Utilities
│   │   ├── hashing.py
│   │   └── jwt.py
│   └── tests/               # Test files
│       ├── test_org_endpoints.py
│       ├── test_auth_endpoints.py
│       ├── test_validation.py
│       └── test_protected_endpoints.py
├── scripts/
│   └── init_db.py           # Database initialization
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline
├── docker-compose.yml
├── dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml          # Tool configurations
├── Makefile
└── README.md
```

## CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline that runs on every push and pull request:

1. **Lint** - Code linting with ruff
2. **Format** - Code formatting check with black
3. **Type Check** - Type checking with mypy
4. **Security** - Security scanning with bandit
5. **Tests** - Unit and integration tests with pytest
6. **Docker Build** - Docker image build and test
7. **API Tests** - End-to-end API testing
8. **Quality Gate** - Ensures all checks pass

## Environment Variables

Create a `.env` file with the following variables:

```env
APP_NAME=Wedding Backend
MONGO_URI=mongodb://mongo:27017
MASTER_DB=master_db
SECRET_KEY=your-secret-key-here
TOKEN_EXPIRE_HOURS=6
```

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing

# Specific test
pytest app/tests/test_org_endpoints.py::test_create_and_get_org
```

### Test Coverage

The project aims for high test coverage. Current coverage includes:

- ✅ Organization CRUD operations
- ✅ Authentication and authorization
- ✅ Input validation
- ✅ Protected endpoints
- ✅ Error handling
- ✅ Database operations

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Input validation with Pydantic
- Security scanning with bandit
- No sensitive data in logs



