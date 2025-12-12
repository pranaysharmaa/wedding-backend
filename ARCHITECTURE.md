# Wedding Backend Architecture

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Database Architecture](#database-architecture)
6. [API Architecture](#api-architecture)
7. [Authentication & Authorization](#authentication--authorization)
8. [Security Architecture](#security-architecture)
9. [Deployment Architecture](#deployment-architecture)
10. [Data Flow](#data-flow)
11. [Component Interactions](#component-interactions)
12. [Scalability & Performance](#scalability--performance)
13. [Error Handling](#error-handling)
14. [Testing Architecture](#testing-architecture)

---

## System Overview

The Wedding Backend is a **multi-tenant SaaS application** built with FastAPI that provides organization management capabilities with isolated data storage per tenant. The system follows a **collection-per-tenant** pattern where each organization gets its own MongoDB collection for data isolation.

### Key Characteristics

- **Multi-tenant Architecture**: Each organization has isolated data storage
- **RESTful API**: RESTful endpoints for all operations
- **JWT Authentication**: Stateless authentication using JWT tokens
- **MongoDB**: NoSQL database for flexible schema and scalability
- **Microservices-ready**: Modular design that can be containerized
- **Production-ready**: Comprehensive testing, security, and CI/CD

---

## Architecture Patterns

### 1. Multi-Tenant Architecture (Collection-per-Tenant)

The system implements a **collection-per-tenant** pattern where:

- Each organization (tenant) has its own MongoDB collection
- Collection naming: `org_{sanitized_org_name}`
- Master database contains metadata collections:
  - `organizations`: Organization metadata
  - `admins`: Admin user accounts

**Benefits:**
- Data isolation at the database level
- Easy tenant data management
- Simple backup and restore per tenant
- Performance isolation between tenants

**Example:**
```
master_db/
├── organizations/          # Master metadata
├── admins/                 # Master admin accounts
├── org_acme_corp/          # Tenant collection
├── org_wedding_planners/   # Tenant collection
└── org_events_inc/          # Tenant collection
```

### 2. Layered Architecture

The application follows a **layered architecture** pattern:

```
┌─────────────────────────────────────┐
│         API Layer (Routes)          │  ← HTTP endpoints, request/response
├─────────────────────────────────────┤
│      Service Layer (Business)       │  ← Business logic, orchestration
├─────────────────────────────────────┤
│      Data Access Layer (Database)    │  ← Database operations, queries
├─────────────────────────────────────┤
│      Utility Layer (Utils)          │  ← Reusable utilities (hashing, JWT)
└─────────────────────────────────────┘
```

**Layer Responsibilities:**

- **Routes Layer** (`app/routes/`): HTTP request handling, validation, response formatting
- **Service Layer** (`app/services/`): Business logic, data transformation, orchestration
- **Data Access Layer** (`app/database.py`): Database connections, queries, data persistence
- **Utility Layer** (`app/utils/`): Reusable functions (password hashing, JWT operations)

### 3. Dependency Injection

FastAPI's dependency injection system is used for:
- Authentication token extraction
- Database connection management
- Service layer access

---

## Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.11**: Latest Python features and performance improvements

### Database
- **MongoDB 6.0**: NoSQL document database
- **PyMongo**: Official MongoDB driver for Python

### Authentication & Security
- **python-jose**: JWT token encoding/decoding
- **bcrypt**: Password hashing (direct implementation)
- **Pydantic**: Data validation and settings management

### Development & Quality
- **pytest**: Testing framework
- **ruff**: Fast Python linter
- **black**: Code formatter
- **mypy**: Static type checker
- **bandit**: Security vulnerability scanner

### Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Uvicorn**: ASGI server

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│                    (Web/Mobile/API Clients)                 │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    API Gateway Layer                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastAPI Application                       │  │
│  │  ┌──────────────┐  ┌──────────────┐                  │  │
│  │  │  CORS Middleware│  │  Auth Middleware│              │  │
│  │  └──────────────┘  └──────────────┘                  │  │
│  │                                                         │  │
│  │  ┌──────────────┐  ┌──────────────┐                  │  │
│  │  │  Org Routes   │  │  Auth Routes │                  │  │
│  │  └──────┬───────┘  └──────┬───────┘                  │  │
│  └─────────┼─────────────────┼──────────────────────────┘  │
└────────────┼─────────────────┼─────────────────────────────┘
             │                 │
    ┌────────▼────────┐ ┌─────▼──────────┐
    │  OrgService     │ │  AuthService   │
    │  (Business Logic)│ │  (Business Logic)│
    └────────┬────────┘ └─────┬──────────┘
             │                 │
    ┌────────▼─────────────────▼──────────┐
    │      Database Layer                  │
    │  ┌──────────────────────────────┐  │
    │  │    MongoDB Connection Pool     │  │
    │  └──────────────┬─────────────────┘  │
    └─────────────────┼────────────────────┘
                      │
    ┌─────────────────▼────────────────────┐
    │         MongoDB Database              │
    │  ┌─────────────────────────────────┐ │
    │  │      master_db                   │ │
    │  │  - organizations (metadata)      │ │
    │  │  - admins (user accounts)        │ │
    │  │  - org_* (tenant collections)    │ │
    │  └─────────────────────────────────┘ │
    └──────────────────────────────────────┘
```

### Component Breakdown

#### 1. Application Entry Point (`app/main.py`)
- FastAPI application initialization
- Middleware configuration (CORS)
- Route registration
- Startup/shutdown event handlers
- Health check endpoint

#### 2. Route Handlers (`app/routes/`)
- **`org.py`**: Organization CRUD operations
- **`auth.py`**: Authentication endpoints

#### 3. Service Layer (`app/services/`)
- **`org_service.py`**: Organization business logic
  - Create, read, update, delete organizations
  - Tenant collection management
  - Data migration on org rename
  
- **`auth_service.py`**: Authentication business logic
  - Admin authentication
  - JWT token generation
  - Token validation

#### 4. Data Access Layer (`app/database.py`)
- MongoDB connection management
- Connection pooling
- Tenant collection utilities
- Name sanitization

#### 5. Utilities (`app/utils/`)
- **`hashing.py`**: Password hashing with bcrypt
- **`jwt.py`**: JWT token creation and validation

---

## Database Architecture

### Database Structure

```
MongoDB Instance
└── master_db (Database)
    ├── organizations (Collection)
    │   └── Documents: { name, collection, admin_id }
    │
    ├── admins (Collection)
    │   └── Documents: { email, password (hashed), org }
    │
    └── org_* (Tenant Collections)
        ├── org_acme_corp
        ├── org_wedding_planners
        └── org_events_inc
```

### Collections Schema

#### 1. `organizations` Collection
```json
{
  "_id": ObjectId("..."),
  "name": "Acme Corp",
  "collection": "org_acme_corp",
  "admin_id": "693c96ab3792ee544c092c9f"
}
```

**Indexes:**
- Unique index on `name` (case-insensitive)

#### 2. `admins` Collection
```json
{
  "_id": ObjectId("..."),
  "email": "admin@acme.com",
  "password": "$2b$12$...",  // bcrypt hash
  "org": "Acme Corp"
}
```

**Indexes:**
- Unique index on `email`

#### 3. Tenant Collections (`org_*`)
- Dynamic collections created per organization
- Schema is flexible (document-based)
- Isolated from other tenants

### Database Operations

#### Connection Management
- **Singleton Pattern**: Single MongoDB client instance
- **Connection Pooling**: Managed by PyMongo
- **Retry Logic**: Automatic retry on connection failures
- **Health Checks**: Ping on startup

#### Tenant Collection Naming
1. Input: `"Acme Corp"`
2. Sanitize: Lowercase, replace special chars with `_`
3. Result: `"org_acme_corp"`

#### Data Isolation Strategy
- **Collection-level isolation**: Each tenant has separate collection
- **No cross-tenant queries**: Queries scoped to specific collection
- **Metadata separation**: Master collections separate from tenant data

---

## API Architecture

### RESTful Design Principles

- **Resource-based URLs**: `/org/{resource}`, `/admin/{resource}`
- **HTTP Methods**: GET, POST, PUT, DELETE
- **Status Codes**: Proper HTTP status codes (200, 201, 400, 401, 404, 422)
- **JSON**: Request/response in JSON format

### API Endpoints

#### Organization Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/org/create` | Create organization | No |
| GET | `/org/get?organization_name={name}` | Get organization | No |
| PUT | `/org/update?current_name={old}&new_name={new}` | Update organization | Yes |
| DELETE | `/org/delete?org_name={name}` | Delete organization | Yes |

#### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/admin/login` | Admin login | No |

### Request/Response Flow

```
Client Request
    │
    ├─► FastAPI Router
    │       │
    │       ├─► Pydantic Validation
    │       │       │
    │       │       └─► Schema Validation (422 if invalid)
    │       │
    │       ├─► Dependency Injection
    │       │       │
    │       │       └─► Auth Token Extraction (if protected)
    │       │
    │       └─► Route Handler
    │               │
    │               └─► Service Layer
    │                       │
    │                       └─► Database Layer
    │                               │
    │                               └─► MongoDB
    │
    └─► Response (JSON)
```

### Validation Architecture

**Pydantic Models** (`app/schemas.py`):
- `OrgCreateRequest`: Organization creation validation
- `OrgMeta`: Organization metadata structure
- `AdminLoginRequest`: Login credentials validation
- `TokenResponse`: JWT token response structure

**Validation Rules:**
- Email format validation
- Password length (min 6 characters)
- Organization name pattern matching
- Required field validation

---

## Authentication & Authorization

### Authentication Flow

```
1. Client sends credentials
   POST /admin/login
   { "email": "...", "password": "..." }
   
2. AuthService.authenticate_admin()
   ├─► Query admins collection
   ├─► Verify password (bcrypt)
   └─► Generate JWT token
   
3. Response with JWT
   {
     "access_token": "eyJhbGc...",
     "token_type": "bearer"
   }
   
4. Client includes token in subsequent requests
   Authorization: Bearer eyJhbGc...
```

### JWT Token Structure

**Payload:**
```json
{
  "admin_id": "693c96ab3792ee544c092c9f",
  "org": "Acme Corp",
  "collection": "org_acme_corp",
  "exp": 1765600123
}
```

**Token Lifecycle:**
- **Creation**: On successful login
- **Validation**: On each protected endpoint request
- **Expiration**: Configurable (default: 6 hours)
- **Storage**: Client-side (stateless)

### Authorization Model

**Role-based Access:**
- **Admin**: Full access to their organization
- **Organization-scoped**: Admins can only access their own org data

**Authorization Checks:**
```python
# In protected endpoints
if admin.get("org") != org_name:
    raise HTTPException(403, "Not authorized for this org")
```

### Password Security

**Hashing Algorithm**: bcrypt
- **Rounds**: Default (12 rounds)
- **Salt**: Auto-generated per password
- **Length Limit**: 72 bytes (truncated if longer)

**Storage**: Never store plaintext passwords

---

## Security Architecture

### Security Layers

#### 1. Input Validation
- **Pydantic**: Schema validation on all inputs
- **Email Validation**: Format checking
- **Password Strength**: Minimum length enforcement
- **SQL Injection Prevention**: Parameterized queries (MongoDB)

#### 2. Authentication Security
- **JWT Tokens**: Stateless, signed tokens
- **Password Hashing**: bcrypt with salt
- **Token Expiration**: Time-limited tokens
- **Secure Headers**: CORS configuration

#### 3. Data Security
- **Data Isolation**: Collection-per-tenant
- **No Cross-tenant Access**: Authorization checks
- **Encrypted Connections**: MongoDB connection security

#### 4. Application Security
- **Dependency Scanning**: Bandit security scanner
- **Code Quality**: Linting and type checking
- **Error Handling**: No sensitive data in error messages

### Security Best Practices

1. **Environment Variables**: Sensitive config in `.env`
2. **Secret Key**: Strong SECRET_KEY for JWT signing
3. **HTTPS**: Recommended for production
4. **Rate Limiting**: Should be added for production
5. **Input Sanitization**: Organization name sanitization

---

## Deployment Architecture

### Docker Architecture

```
┌─────────────────────────────────────────┐
│         Docker Compose Network          │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │  Web Service │    │  Mongo DB     │  │
│  │  (FastAPI)   │◄───┤  (Database)   │  │
│  │  Port: 8000  │    │  Port: 27017  │  │
│  └──────────────┘    └──────────────┘  │
│                                         │
│  ┌──────────────┐                      │
│  │  Init-DB     │                      │
│  │  (One-shot)  │                      │
│  └──────────────┘                      │
└─────────────────────────────────────────┘
```

### Container Structure

#### Web Container
- **Base Image**: `python:3.11-slim`
- **Working Directory**: `/app`
- **Port**: 8000
- **Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Volumes**: 
  - `./app:/app/app` (development hot-reload)
  - `./scripts:/app/scripts`

#### MongoDB Container
- **Image**: `mongo:6.0`
- **Port**: 27017
- **Volume**: `mongo_data` (persistent storage)
- **Database**: `master_db`

### Environment Configuration

**Configuration Sources** (priority order):
1. Environment variables
2. `.env` file
3. Default values in `Settings` class

**Key Settings:**
- `MONGO_URI`: MongoDB connection string
- `MASTER_DB`: Master database name
- `SECRET_KEY`: JWT signing key
- `TOKEN_EXPIRE_HOURS`: Token expiration time

---

## Data Flow

### Organization Creation Flow

```
1. Client → POST /org/create
   {
     "organization_name": "Acme Corp",
     "email": "admin@acme.com",
     "password": "secure123"
   }

2. Route Handler (org.py)
   ├─► Validate input (Pydantic)
   └─► Call OrgService.create_org()

3. Service Layer (org_service.py)
   ├─► Check org name uniqueness
   ├─► Create tenant collection: org_acme_corp
   ├─► Hash password (bcrypt)
   ├─► Create admin document
   └─► Create organization document

4. Database
   ├─► Insert into admins collection
   ├─► Insert into organizations collection
   └─► Create org_acme_corp collection

5. Response → Client
   {
     "name": "Acme Corp",
     "collection": "org_acme_corp",
     "admin_email": "admin@acme.com"
   }
```

### Authentication Flow

```
1. Client → POST /admin/login
   {
     "email": "admin@acme.com",
     "password": "secure123"
   }

2. Route Handler (auth.py)
   ├─► Validate input
   └─► Call AuthService.authenticate_admin()

3. Service Layer (auth_service.py)
   ├─► Query admins collection by email
   ├─► Verify password (bcrypt.checkpw)
   ├─► Get organization details
   ├─► Generate JWT token
   └─► Return token

4. Response → Client
   {
     "access_token": "eyJhbGc...",
     "token_type": "bearer"
   }
```

### Protected Endpoint Flow

```
1. Client → PUT /org/update
   Headers: Authorization: Bearer eyJhbGc...
   Query: current_name=old&new_name=new

2. Route Handler (org.py)
   ├─► Extract token (Dependency: require_admin)
   └─► Call OrgService.update_org_name()

3. Dependency (dependencies.py)
   ├─► Extract Bearer token from header
   ├─► Decode JWT token
   └─► Validate token and return admin payload

4. Service Layer (org_service.py)
   ├─► Verify admin belongs to org
   ├─► Check new name availability
   ├─► Copy data from old collection to new
   ├─► Update organization metadata
   ├─► Update admin org references
   └─► Drop old collection

5. Response → Client
   {
     "old_name": "old",
     "new_name": "new",
     "new_collection": "org_new",
     "moved_docs": 42
   }
```

---

## Component Interactions

### Request Processing Sequence

```
┌─────────┐
│ Client  │
└────┬────┘
     │ HTTP Request
     ▼
┌─────────────────┐
│  FastAPI App    │
│  (main.py)      │
└────┬────────────┘
     │
     ├─► CORS Middleware
     │
     ├─► Route Matching
     │
     ├─► Dependency Injection
     │   └─► Auth Token Extraction (if needed)
     │
     ├─► Pydantic Validation
     │   └─► Schema Validation
     │
     └─► Route Handler
         │
         ├─► Service Layer Call
         │   │
         │   ├─► Business Logic
         │   │
         │   └─► Database Operations
         │       │
         │       ├─► Connection Pool
         │       │
         │       └─► MongoDB Query
         │
         └─► Response Formation
             │
             └─► JSON Response
```

### Service Layer Interactions

```
Route Handler
    │
    ├─► OrgService
    │   ├─► get_master_db()
    │   ├─► tenant_collection_name()
    │   ├─► create_tenant_collection()
    │   └─► hash_password()
    │
    └─► AuthService
        ├─► get_master_db()
        ├─► verify_password()
        └─► create_access_token()
```

---

## Scalability & Performance

### Current Architecture Scalability

#### Horizontal Scaling
- **Stateless API**: Can run multiple instances
- **MongoDB Replication**: Support for replica sets
- **Load Balancing**: Multiple FastAPI instances behind load balancer

#### Vertical Scaling
- **Connection Pooling**: MongoDB connection reuse
- **Async Operations**: FastAPI async support (can be extended)
- **Caching**: Can add Redis for session/token caching

### Performance Optimizations

1. **Database Indexes**
   - Unique index on `organizations.name`
   - Unique index on `admins.email`

2. **Connection Management**
   - Singleton MongoDB client
   - Connection pooling
   - Retry logic for resilience

3. **Batch Operations**
   - Bulk document copying during org rename
   - Batch size: 500 documents

### Scalability Considerations

**Current Limitations:**
- Single MongoDB instance (can be scaled to replica set)
- No caching layer (can add Redis)
- Synchronous operations (can be made async)

**Future Enhancements:**
- MongoDB sharding for large datasets
- Redis caching for frequently accessed data
- Async database operations
- CDN for static assets (if added)

---

## Error Handling

### Error Handling Strategy

#### 1. Validation Errors (422)
- **Source**: Pydantic validation
- **Response**: Detailed field-level errors
- **Example**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error"
    }
  ]
}
```

#### 2. Business Logic Errors (400, 404)
- **Source**: Service layer
- **Response**: User-friendly error messages
- **Examples**:
  - 400: "Organization already exists"
  - 404: "Organization not found"

#### 3. Authentication Errors (401)
- **Source**: Auth service/dependencies
- **Response**: Generic error (security)
- **Examples**:
  - "Authorization header missing"
  - "Invalid credentials"
  - "Invalid token"

#### 4. Authorization Errors (403)
- **Source**: Route handlers
- **Response**: Access denied message
- **Example**: "Not authorized for this org"

#### 5. Server Errors (500)
- **Source**: Unexpected exceptions
- **Response**: Generic error (no sensitive data)
- **Logging**: Full error details in logs

### Error Flow

```
Exception Raised
    │
    ├─► HTTPException (FastAPI)
    │   └─► Returns appropriate status code
    │
    ├─► ValidationError (Pydantic)
    │   └─► Returns 422 with details
    │
    └─► Unexpected Exception
        └─► Returns 500 (logged, not exposed)
```

---

## Testing Architecture

### Test Structure

```
app/tests/
├── test_org_endpoints.py      # Organization CRUD tests
├── test_auth_endpoints.py     # Authentication tests
├── test_validation.py          # Input validation tests
└── test_protected_endpoints.py # Authorization tests
```

### Testing Strategy

#### 1. Unit Tests
- **Scope**: Individual functions/methods
- **Tools**: pytest
- **Coverage**: Business logic, utilities

#### 2. Integration Tests
- **Scope**: API endpoints with database
- **Tools**: pytest + TestClient
- **Coverage**: End-to-end request/response

#### 3. API Tests
- **Scope**: Full API workflow
- **Tools**: curl/bash scripts
- **Coverage**: Real HTTP requests

### Test Data Management

- **Isolation**: Each test cleans up its data
- **Teardown**: Module-level cleanup functions
- **Naming**: Test data prefixed with `test_`
- **Database**: Uses same MongoDB instance (test isolation via naming)

### CI/CD Testing

**Automated Tests:**
1. Unit tests (pytest)
2. Integration tests (pytest)
3. API tests (bash script)
4. Code coverage reporting
5. Security scanning (bandit)

---

## Architecture Decisions

### Why Collection-per-Tenant?

**Pros:**
- ✅ Strong data isolation
- ✅ Easy backup/restore per tenant
- ✅ Simple data migration
- ✅ Performance isolation

**Cons:**
- ❌ More collections to manage
- ❌ Potential MongoDB collection limit (but very high)

**Alternative Considered:** Row-level isolation (single collection with tenant_id)
- Rejected due to weaker isolation and complexity

### Why FastAPI?

**Pros:**
- ✅ Modern async support
- ✅ Automatic API documentation
- ✅ Type hints and validation
- ✅ High performance
- ✅ Easy to learn

### Why MongoDB?

**Pros:**
- ✅ Flexible schema (good for multi-tenant)
- ✅ Horizontal scaling
- ✅ Document model fits tenant data
- ✅ Easy collection management

### Why JWT?

**Pros:**
- ✅ Stateless (no server-side session storage)
- ✅ Scalable (works across instances)
- ✅ Self-contained (includes user info)
- ✅ Industry standard

---

## Future Enhancements

### Potential Improvements

1. **Caching Layer**
   - Redis for frequently accessed data
   - Token blacklisting
   - Organization metadata caching

2. **Async Operations**
   - Async database operations
   - Background tasks for heavy operations
   - WebSocket support

3. **Advanced Features**
   - Multi-admin support per organization
   - Role-based access control (RBAC)
   - Audit logging
   - Rate limiting

4. **Monitoring & Observability**
   - Application metrics (Prometheus)
   - Distributed tracing
   - Log aggregation
   - Health check endpoints

5. **Database Enhancements**
   - MongoDB replica sets
   - Sharding for scale
   - Read replicas

---

## Conclusion

The Wedding Backend architecture is designed for:

- **Scalability**: Multi-tenant, stateless design
- **Security**: Strong isolation, authentication, validation
- **Maintainability**: Clean layers, separation of concerns
- **Reliability**: Error handling, retry logic, testing
- **Performance**: Connection pooling, efficient queries

The architecture supports current requirements while providing a foundation for future growth and enhancements.

---



