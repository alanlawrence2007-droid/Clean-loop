# Clean Loop - AI-Assisted Smart Waste Management Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready backend for smart waste management with AI-powered classification, complaint tracking, facility discovery, and municipal analytics.

## 🌟 Features

- **🔐 Authentication & Authorization** - JWT-based auth with role-based access (Citizen, Staff, Admin)
- **🗑️ Waste Classification** - AI-powered waste categorization with disposal instructions
- **🏢 Facility Management** - Location-based facility discovery with PostGIS support
- **📝 Complaint System** - Complete complaint lifecycle with status history tracking
- **📴 Offline Support** - Sync complaints created offline with duplicate prevention
- **📊 Analytics Dashboard** - Municipal-level insights and complaint hotspot identification
- **✅ Facility Verification** - Distinguish verified vs unverified facilities
- **📸 Image Support** - Photo URL support for complaints (Cloudinary ready)

## 📋 Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+ with PostGIS extension
- pip or poetry for package management

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd clean-loop

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb cleanloop

# Enable PostGIS extension (run in psql)
psql -d cleanloop -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Update DATABASE_URL, SECRET_KEY, etc.
```

### 4. Run Migrations

```bash
# Initialize Alembic (if not already done)
alembic upgrade head
```

### 5. Seed Database

```bash
# Run seed script to populate initial data
python scripts/seed_data.py
```

### 6. Run the Server

```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access the API

- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **API Base URL**: http://localhost:8000/api/v1

## 📚 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT token |
| GET | `/api/v1/auth/me` | Get current user profile |

### Waste Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/waste/categories` | Get all waste categories |
| POST | `/api/v1/waste/classify` | Classify waste item (AI) |
| GET | `/api/v1/waste/rules` | Get disposal rules |
| GET | `/api/v1/waste/rules/{category_id}` | Get rules by category |

### Facilities
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/facilities` | Get all facilities (paginated) |
| GET | `/api/v1/facilities/nearby` | Find nearby facilities |
| GET | `/api/v1/facilities/{id}` | Get facility details |

### Complaints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/complaints` | Create complaint |
| GET | `/api/v1/complaints/mine` | Get user's complaints |
| GET | `/api/v1/complaints/{id}` | Get complaint details |
| PATCH | `/api/v1/complaints/{id}/status` | Update status (Staff/Admin) |
| POST | `/api/v1/complaints/{id}/feedback` | Submit feedback |
| GET | `/api/v1/complaints` | Get all complaints (Staff/Admin) |
| POST | `/api/v1/sync/complaints` | Offline sync |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/overview` | Dashboard overview (Staff/Admin) |
| GET | `/api/v1/analytics/hotspots` | Complaint hotspots (Staff/Admin) |

## 👥 User Roles

| Role | Permissions |
|------|------------|
| **citizen** | Submit complaints, view facilities, track own complaints, submit feedback |
| **municipal_staff** | All citizen permissions + update complaint status, view all complaints, access analytics |
| **admin** | Full system access |

## 🔒 Test Credentials

After running the seed script:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@cleanloop.gov | admin12345 |
| Staff | staff1@cleanloop.gov | staff12345 |
| Citizen | citizen1@example.com | citizen12345 |

## 🗄️ Database Schema

### Core Tables

- **users** - User accounts with role-based access
- **waste_categories** - Waste classification categories
- **disposal_rules** - Locality-specific disposal guidelines
- **facilities** - Waste management facilities with location
- **complaints** - User complaints with full tracking
- **complaint_status_history** - Complete status change audit trail
- **feedbacks** - User feedback on resolved complaints

## 🛠️ Development

### Project Structure

```
app/
├── main.py              # FastAPI application
├── core/
│   ├── config.py        # Settings and configuration
│   ├── database.py      # Database connection
│   └── security.py      # Auth utilities
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── api/v1/
│   ├── endpoints/       # API route handlers
│   └── api.py           # Router configuration
├── services/            # Business logic
└── utils/               # Helper utilities
```

### Running Tests

```bash
# Run tests (when implemented)
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint
flake8 app/
```

## 📦 Key Dependencies

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy 2.0** - Async ORM with type hints
- **Pydantic v2** - Data validation
- **Alembic** - Database migrations
- **PostGIS** - Geospatial queries
- **python-jose** - JWT handling
- **passlib[bcrypt]** - Password hashing

## 🌍 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://...` |
| `SECRET_KEY` | JWT secret key | *Required* |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | `30` |
| `CORS_ORIGINS` | Allowed origins | `["http://localhost:3000"]` |

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ for cleaner cities and smarter waste management.
