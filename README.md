# ProcureGov — Public Sector Procurement & Bidding Platform

A secure, transparent web-based procurement platform built with Django for government agencies and vendors. Developed as a final project for BSIT at Eastern Visayas State University (EVSU).

**Live Demo:** https://procuregov.onrender.com

---

## Overview

ProcureGov digitizes the public procurement process by providing a transparent platform where government agencies can post procurement opportunities, vendors can submit sealed bids, and the public can monitor awarded contracts — all in one place.

---

## Features

### Public
- Browse all procurement listings with search and filter
- View procurement details with live countdown timer
- View all awarded contracts (winning vendor publicly disclosed)

### Vendor
- Register and await admin verification
- Submit sealed bids (amounts hidden until bid opening date)
- Track personal bid history and status

### Agency Admin
- Full procurement CRUD dashboard
- View all bids per procurement after opening date
- Award contracts to winning vendors

### Superuser (System Admin)
- Verify, reject, or revoke vendor accounts
- Manage government agencies
- Full access to Django admin panel

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 6.0.5 |
| REST API | Django REST Framework, SimpleJWT |
| Frontend | Bootstrap 5.3, Bootstrap Icons, Vanilla JS |
| Database (dev) | SQLite |
| Database (prod) | PostgreSQL (Render) |
| Media storage | Cloudinary |
| Static files | WhiteNoise |
| Authentication | Django Auth + django-axes (brute force protection) |
| Deployment | Render |

---

## Project Structure
procurement_platform/
├── config/
│   ├── settings/
│   │   ├── base.py       ← shared settings
│   │   ├── dev.py        ← local development
│   │   └── prod.py       ← production (Render)
│   └── urls.py
├── users/                ← CustomUser, auth, vendor verification
├── procurements/         ← Agency, Procurement models + CRUD
├── bids/                 ← Bid, Award models + sealed bidding
├── api/                  ← DRF serializers + JWT endpoints
├── audit/                ← NIST audit logging
├── templates/
├── static/
├── build.sh              ← Render build script
└── requirements.txt
---

## Security Features

- **Sealed bidding** — bid amounts hidden until `bid_open_date` passes
- **Anti-IDOR** — `BidManager.visible_to()` prevents vendors seeing other bids
- **Brute force protection** — django-axes locks accounts after failed attempts
- **Honeypot field** — bot detection on bid submission form
- **JWT authentication** — stateless API auth with access/refresh tokens
- **Role-based access control** — AGENCY_ADMIN, VENDOR, PUBLIC roles
- **CSRF protection** — all forms protected
- **Security headers** — HSTS, XFrame, XSS, Content-Type in production
- **Audit logging** — NIST-style event log for bid submissions and contract awards

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/token/` | None | Get JWT access + refresh tokens |
| POST | `/api/auth/token/refresh/` | None | Refresh access token |
| GET | `/api/me/` | Bearer | Current user info |
| GET | `/api/procurements/` | None | List all procurements |
| GET | `/api/procurements/<pk>/` | None | Procurement detail |
| GET | `/api/procurements/<pk>/bids/` | Bearer | List bids (role-filtered) |
| POST | `/api/procurements/<pk>/bids/submit/` | Verified Vendor | Submit a bid |
| GET | `/api/bids/mine/` | Verified Vendor | My submitted bids |
| GET | `/api/awards/` | None | All awarded contracts |

---

## Local Development Setup

### Prerequisites
- Python 3.12
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/procurement-platform.git
cd procurement-platform

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
echo "DJANGO_SETTINGS_MODULE=config.settings.dev" > .env
echo "DJANGO_SECRET_KEY=your-dev-secret-key" >> .env

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000`

---

## User Roles & Test Accounts

| Role | Access |
|---|---|
| Superuser | `/admin`, `/admin-panel/`, full system access |
| Agency Admin | `/dashboard/`, procurement CRUD, bid viewing, awarding |
| Vendor | Browse procurements, submit bids, view own bids |
| Public | Browse procurements, view awarded contracts |

To create test accounts use Django shell:
```bash
python manage.py shell
```

---

## Deployment (Render)

### Environment Variables Required

| Key | Description |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.prod` |
| `DJANGO_SECRET_KEY` | Strong random secret key |
| `DATABASE_URL` | Render PostgreSQL connection string |
| `ALLOWED_HOSTS` | `your-app.onrender.com` |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |

### Build Command
./build.sh

### Start Command
gunicorn config.wsgi:application

---

## Security Scan Results

| Tool | Finding | Severity | Resolution |
|---|---|---|---|
| bandit | Hardcoded SECRET_KEY in base.py | Low | Moved to environment variable |
| bandit | Hardcoded SECRET_KEY in dev.py | Low | Accepted — dev only |
| manage.py check --deploy | HSTS not configured | Medium | Fixed in prod.py |
| manage.py check --deploy | SSL redirect not set | Medium | Fixed in prod.py |
| manage.py check --deploy | SESSION_COOKIE_SECURE | Medium | Fixed in prod.py |
| manage.py check --deploy | CSRF_COOKIE_SECURE | Medium | Fixed in prod.py |
| manage.py check --deploy | DEBUG=True | High | Fixed — False in prod.py |
| manage.py check --deploy | Weak SECRET_KEY | High | Fixed — env variable |
| pip-audit | Network unavailable | N/A | School network restriction |

---

## Developer

**Mark Gerard** — BSIT Student, Eastern Visayas State University (EVSU)

Final Project — Information Assurance and Security / Web Systems

---

## License

This project is for academic purposes only.