# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based backend API for a "Headless Open ERP" application. It implements a lead management system with contact tracking, notes, fingerprinting, and reporting capabilities. The application uses PostgreSQL in production and SQLite for development/testing.

## Architecture

The codebase follows a **layered architecture** (Clean/Hexagonal Architecture) with three main layers:

- **Domain Layer** (`domain/`): Core business logic and entities
  - `orm.py`: SQLAlchemy ORM models (database tables)
  - `contact.py`: Pydantic models for API request/response validation

- **Application Layer** (`application/`): Business rules and use case orchestration
  - Services follow the pattern `*_service.py` (e.g., `contact_service.py`, `note_service.py`)
  - Each service encapsulates logic for a specific business domain

- **Infrastructure Layer** (`infrastructure/`): External concerns (web, database, mail)
  - `web/app.py`: Main FastAPI application and endpoint definitions
  - `database.py`: SQLAlchemy database connection configuration
  - `mail/sender.py`: Email notification service
  - `web/auth.py`: OIDC authentication using JWT tokens

## Development Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Development server with auto-reload
uvicorn infrastructure.web.app:app --reload

# Production server (Docker)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker infrastructure.web.wsgi:app -b 0.0.0.0:8000
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_apibase.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=.
```

### Database Migrations
```bash
# Run migrations programmatically (happens automatically on app startup)
python run_migrations.py

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations manually
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Environment Configuration

Create a `.env` file with the following variables:
- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:password@host:port/database`)
- `AUTHORIZED_ORIGINS`: Comma-separated list of allowed CORS origins
- `MAIL_FROM`: Email sender address
- `MAIL_TO`: Email recipient address
- `ALTCHA_HMAC_KEY`: HMAC key for ALTCHA challenge verification
- `OIDC_CLIENT_SECRET`: OAuth/OIDC client secret
- `OIDC_ISSUER_URL`: OAuth/OIDC provider URL (also via `OCTOBRE_ISSUER_URL`)
- `ENV`: Set to `pytest` for test environment

## Key Technical Details

### Database Setup
- **Production**: Uses PostgreSQL (via `DATABASE_URL` environment variable)
- **Development**: Uses SQLite (`dev.db` in project root)
- **Testing**: Uses SQLite (`test.db` in project root, `ENV=pytest`)
- Database URL is automatically converted from `postgres://` to `postgresql://` for SQLAlchemy compatibility
- Migrations run automatically on app startup (except in test environment)

### Authentication
- Protected endpoints use OIDC/OAuth2 with JWT tokens
- Token validation via `get_current_user` dependency
- Fetches JWKS from OIDC provider's well-known endpoint
- Test mode overrides authentication dependencies

### API Security
- Public endpoints (lead creation, fingerprinting, reporting) require ALTCHA challenge verification
- ALTCHA prevents bot submissions without CAPTCHA UX friction
- Protected endpoints require valid JWT token in Authorization header

### Core Domain Models
- **Lead**: Central entity representing sales leads with relationships to Contact, Company, Position, Concern, Notes, etc.
- **Lead.potential_score**: Hybrid property that calculates lead quality based on company size, urgency, and contact job title
- **Contact**: People associated with leads
- **Company**: Organizations associated with leads
- **Note**: Comments/interactions on leads with reason tracking
- **Fingerprint**: Browser fingerprint tracking for visitor identification
- **Report**: Page visit tracking linked to fingerprints
- **EmailAccount**: IMAP server configurations for multiple email accounts (host, port, username, password, SSL settings)
- **ClassifiedEmail**: Email metadata with LLM classification (classification text, emergency_level 1-5 scale, abstract 200 chars max), identified by IMAP account + IMAP ID, with optional lead relationship
- **EmailClassificationHistory**: Re-classification tracking with previous values and change reasons

### Service Layer Patterns
- Services receive database session via dependency injection
- `LeadService`: CRUD operations for leads, includes `get_all_leads()` and `get_lead_by_id()`
- `NoteService`: Note management with email notification integration
- `FingerprintService`: Visitor fingerprint storage
- `ReportService`: Page visit tracking (only creates reports if fingerprint exists)
- `EmailNotificationService`: Wraps email sender for business logic notifications
- `EmailAccountService`: CRUD operations for IMAP account configurations (create, read, update, delete email accounts)
- `ClassifiedEmailService`: Email classification management with validation (emergency level 1-5, abstract 200 chars max), automatic history logging on re-classification, query filtering by account/emergency/classification/lead

### Testing Strategy
- Tests use session-scoped fixtures with SQLite database
- Database is created and seeded with enum values at session start
- Authentication dependencies overridden in test environment
- ALTCHA verification bypassed when `ENV=pytest`
