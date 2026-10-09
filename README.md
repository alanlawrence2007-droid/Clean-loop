# Clean Loop

**AI-Assisted Smart Waste Management Platform**

Clean Loop connects citizens and municipal authorities. Citizens can identify waste, get verified local disposal guidance, find facilities, check collection times, report cleanliness issues, and track resolutions. Municipal staff get a dashboard to triage, assign, and resolve complaints.

This repository documents both parts of the platform:

| Part | Description | Stack |
|------|-------------|-------|
| **Backend** | REST API served at `/api/v1` | FastAPI, PostgreSQL + PostGIS |
| **Frontend** | Citizen mobile-first app + municipal admin dashboard | React 18, Vite, TypeScript |

---

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Backend](#backend)
- [Frontend](#frontend)
- [Product Honesty Rules](#product-honesty-rules)
- [Roles](#roles)
- [License](#license)

---

## Features

- User authentication (JWT based)
- Role-based access (Citizen, Municipal Staff, Admin)
- Waste classification and disposal guidance (clearly labelled AI estimates)
- Facility finder with nearby search
- Collection schedules (official schedule, pattern estimate, live GPS kept separate)
- Complaint reporting, status tracking, and history
- Offline-first sync for complaints and facility reports
- Municipal analytics dashboard
- Multilingual UI: English, Hindi, Marathi

## Architecture Overview

```
┌──────────────────────────┐        HTTPS / JSON        ┌──────────────────────────┐
│  Frontend (React + Vite) │  ───────────────────────►  │  Backend (FastAPI)       │
│  - Citizen app (390px)   │       /api/v1  (JWT)       │  - Auth, Waste, Facility │
│  - Admin dashboard       │  ◄───────────────────────  │  - Complaints, Sync      │
│  - IndexedDB offline     │                            │  - Analytics             │
│  - MSW mocks (dev only)  │                            │  PostgreSQL + PostGIS    │
└──────────────────────────┘                            └──────────────────────────┘
```

---

# Backend

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL + PostGIS
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Authentication:** JWT (python-jose + passlib)
- **Validation:** Pydantic v2
- **Language:** Python 3.11+

## Project Structure

```
app/
├── main.py
├── core/
│   ├── config.py
│   ├── database.py
│   └── security.py
├── models/
├── schemas/
├── api/
│   └── v1/
│       ├── endpoints/
│       └── api.py
├── services/
└── utils/
```


## API Documentation

After starting the server, visit:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## Main API Endpoints

### Authentication

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Waste

- `GET /api/v1/waste/categories`
- `POST /api/v1/waste/classify`
- `GET /api/v1/waste/rules`

### Facilities

- `GET /api/v1/facilities`
- `GET /api/v1/facilities/nearby`
- `POST /api/v1/facilities/{id}/reports`

### Collection

- `GET /api/v1/collection/schedules/{locality_id}`
- `GET /api/v1/collection/vehicles/nearby`
- `POST /api/v1/collection/reports`

### Complaints

- `POST /api/v1/complaints`
- `GET /api/v1/complaints/mine`
- `GET /api/v1/complaints/{id}`
- `PATCH /api/v1/complaints/{id}/status`
- `POST /api/v1/complaints/{id}/feedback`
- `POST /api/v1/complaints/{id}/reopen`

### Sync & Analytics

- `POST /api/v1/sync/complaints`
- `POST /api/v1/sync/reports`
- `GET /api/v1/analytics/overview`
- `GET /api/v1/analytics/hotspots`

### Admin

- `GET /api/v1/admin/dashboard/summary`
- `GET /api/v1/admin/analytics/*`
- `GET /api/v1/admin/complaints` (plus assign and status actions)

> **Note:** The frontend spec references a few endpoints (collection, reopen, `sync/reports`, admin routes, `complaints/my`) that go beyond the original backend list. Align these paths between both sides before integration.

---

# Frontend

## Tech Stack

- React 18 + Vite + TypeScript
- Tailwind CSS
- React Router
- TanStack Query
- react-i18next (English, Hindi, Marathi)
- Zod (API response validation)
- idb (IndexedDB)
- Vitest + React Testing Library
- Playwright (3 key user flows)
- MSW (mock service worker, demo data only)

**Viewport targets**

- Citizen app: mobile-first, designed at 390 px
- Admin dashboard: responsive (min 360 px, designed at 1280 px)

## Design Tokens

Configured in `tailwind.config`.

**Fonts**

- Headings: Sora (weights 600–800)
- Body: Manrope
- Hindi/Marathi fallback: Noto Sans Devanagari

**Brand colors**

| Token | Hex |
|-------|-----|
| forest | `#0B3D32` |
| forest-2 | `#10503F` |
| lime | `#C6F36B` |
| ground | `#F2F5F1` |
| ink | `#10231D` |
| muted | `#4B6158` |
| border | `#DCE5E0` |

**Waste category colors**

| Category | Solid | Tint | Dark text |
|----------|-------|------|-----------|
| Wet | `#2E9E5B` | `#DFF3E7` | `#0B4A28` |
| Dry | `#2D6CDF` | `#E1EBFC` | `#123E8F` |
| E-waste | `#7B4FD6` | `#ECE4FA` | `#3D1E8A` |
| Hazardous | `#D9402F` | `#FBE3E0` | `#8A1F14` |
| Sanitary | `#E08A00` | `#FFEFD2` | `#6B4000` |
| Reuse | `#0E8F9B` | `#DDF3F5` | `#0A5760` |


## License

This project is developed for hackathon purposes.
