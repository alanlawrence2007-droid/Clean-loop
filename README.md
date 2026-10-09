# Clean Loop - Smart Waste Management Platform

An AI-assisted smart waste management platform for municipalities featuring waste classification, complaint tracking, facility discovery, and analytics dashboard.

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

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/clean-loop.git
   cd clean-loop
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   # Create PostGIS extension in your PostgreSQL database
   psql -U postgres -d cleanloop -c "CREATE EXTENSION IF NOT EXISTS postgis;"
   
   # Run migrations
   alembic upgrade head
   ```

6. **Load seed data (optional but recommended)**
   ```bash
   python scripts/seed_data.py
   ```

7. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

8. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - ReDoc Documentation: http://localhost:8000/redoc
   - API Base URL: http://localhost:8000/api/v1

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
|------|-------------|
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
| DATABASE_URL | Async PostgreSQL connection string | `postgresql+asyncpg://user:password@localhost/dbname` |
| SECRET_KEY | JWT secret key | Required |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiry | 30 |
| CORS_ORIGINS | Allowed origins | `["http://localhost:3000"]` |
| SUPABASE_URL | Supabase project URL | Optional |
| SUPABASE_KEY | Supabase anon key | Optional |
| SUPABASE_SERVICE_KEY | Supabase service role key | Optional |
| SUPABASE_JWT_SECRET | Supabase JWT secret | Optional |
| STORAGE_BUCKET | Supabase storage bucket | `complaint-images` |

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- Built with FastAPI and modern Python practices
- Inspired by smart city initiatives worldwide
- Special thanks to open-source community contributions