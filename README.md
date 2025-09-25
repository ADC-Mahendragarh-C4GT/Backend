# Suvidha Manch - Django Backend (C4GT 2025)

A Django REST API backend for infrastructure works tracking and audit logging. It manages roads, contractors, infrastructure works, periodic updates with media, comments, inter-department requests, and a custom user system with JWT auth and robust audit trails.

## Tech Stack
- Python, Django 5, Django REST Framework
- JWT auth via djangorestframework-simplejwt
- PostgreSQL
- CORS via django-cors-headers
- Media upload (images, PDFs) with Base64 support

## Project Structure
- `backend/` – Django project settings and URLs
- `accounts/` – Custom user model, auth endpoints, password reset, emails
- `core/` – Domain models (Road, Contractor, InfraWork, Update, Comments, OtherDepartmentRequest) and CRUD APIs
- `audit/` – Audit log models and reporting API
- `media/` – Uploaded images and PDFs (served via `MEDIA_URL`)

## Quick Start
1. Create and activate a virtualenv (recommended)
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables (see .env section below)
4. Apply migrations and create a superuser:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. Run the server:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

By default media is served at `/media/` and APIs under `/` (core), `/accounts/`, `/audit/`.

## Environment Variables (.env)
The app uses `django-environ`. Create a `.env` file in the repo root with at least:

```env
# Django
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
TIME_ZONE=Asia/Kolkata

# Database (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Pagination and CORS
DEFAULT_PAGE_SIZE=20
CORS_ALLOWED_ORIGINS=http://localhost:3000
CORS_ALLOW_CREDENTIALS=True

# Choice lists (value:Label, comma-separated)
USER_TYPE_CHOICES=JE:Junior Engineer,AE:Assistant Engineer,XEN:Executive Engineer,SE:Superintending Engineer,CE:Chief Engineer,JCMC:Joint Commissioner,CMC:Commissioner
ROAD_CATEGORY_CHOICES=NH:National Highway,SH:State Highway,Other:Other
ROAD_TYPE_CHOICES=Asphalt:Asphalt,Concrete:Concrete,Other:Other
MATERIAL_TYPE_CHOICES=Bitumen:Bitumen,RCC:RCC,Other:Other

# JWT
SIMPLE_JWT_ACCESS_TOKEN_LIFETIME=60
SIMPLE_JWT_REFRESH_TOKEN_LIFETIME=7
SIMPLE_JWT_ROTATE_REFRESH_TOKENS=False
SIMPLE_JWT_BLACKLIST_AFTER_ROTATION=True
SIMPLE_JWT_UPDATE_LAST_LOGIN=False

# URLs
SITE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Email (SMTP via Gmail by default)
EMAIL_PORT=587
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=app_password
SENDERS_EMAIL=your@gmail.com
DEFAULT_FROM_EMAIL=${EMAIL_HOST_USER}

# Email templates (use \n for newlines)
EMAIL_TEMPLATE_FOR_STATUS_EMAIL=Hello {department_name},\nStatus: {status}\nRoad: {road_code} - {road_name}\nDescription: {work_description}\nResponse by: {response_by}
EMAIL_TEMPLATE_FOR_NEW_REQUEST=New Request from {requestedBy} ({departmentName}) for {road_code} - {road_name} in {district}, {state}.\nContact: {contactInfo}\nWork: {workDescription}
WELCOME_EMAIL_TEMPLATE=Welcome {first_name}!\nVisit: {frontend_url}
```

Notes:
- `USER_TYPE_CHOICES` and road choice lists are parsed from `value:Label` pairs.
- Media files are saved under `media/` and automatically exposed at `/media/` in development.

## Authentication
- Default permission class is `IsAuthenticated` and JWT authentication is enabled globally.
- Obtain tokens via `POST /accounts/login/` and refresh via `POST /accounts/token/refresh/`.
- Some endpoints are open: registration, user types, password reset flows, welcome email, selected core endpoints as noted.

## Key Endpoints
Base URLs are relative to `SITE_URL` (default `http://localhost:8000`).

### Accounts
- `POST /accounts/register/` – Create user
- `POST /accounts/login/` – JWT login (requires `email`, `password`, `user_type`)
- `GET /accounts/profile/` – Current user profile (auth)
- `POST /accounts/logout/` – Logout (auth)
- `GET /accounts/user-types/` – List of user types
- `PATCH /accounts/updateUser/{user_id}/` – Update another user, with `login_user` actor
- `GET /accounts/Users/` – List users (auth)
- `GET /accounts/UsersWithoutAuth/` – List users (public)
- `GET /accounts/get-login-user/?id={id}` – Get active user by id (auth)
- `DELETE /accounts/deleteUser/{user_id}/` – Soft delete user (auth, logs)
- `POST /accounts/request-password-reset/`
- `GET /accounts/validate-reset-token/{uid}/{token}/`
- `POST /accounts/reset-password/{uid}/{token}/`
- `POST /accounts/send-welcome-email/`

### Core (router under `/api/`)
- `GET/POST /api/roads/` – Roads
- `PATCH/DELETE /api/roads/{id}/` – Updates soft-delete with audit
- `GET/POST /api/contractors/` – Contractors (auth)
- `PATCH/DELETE /api/contractors/{id}/`
- `GET/POST /api/infra-works/` – Infra works (auth)
  - `GET /api/infra-works/{id}/updates/` – Updates for a work
- `GET/POST /api/updates/` – Work updates (auth)
- `GET/POST /api/comments/` – Comments; `DELETE` marks inactive and logs
- `GET/POST /api/other-department-requests/` – Create public, others auth
- `GET /api/InfraWorksbyRoad/?road_id={id}` – List works by road
- `GET /api/updatesPage/` – List infra works by start date
- `POST /upload-csv/` – Bulk create roads from CSV (auth)
- Emails:
  - `POST /send-xen-email/`
  - `POST /send-status-email/{id}/`

### Audit
- `GET /audit/report/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` – Aggregated logs across models

## Models Overview
- `accounts.CustomUser` – Extends `AbstractUser` with `user_type`, `phone_number`, `isActive`
- `core.Road`, `core.Contractor`, `core.InfraWork`, `core.Update`, `core.Comments`, `core.OtherDepartmentRequest`
- `audit.*AuditLog` – One per domain entity; captures action, actor, snapshots, timestamp

## Media Handling
- Images: Base64 via `drf-extra-fields` `Base64ImageField`
- PDFs: Base64 via custom `Base64PdfFileField` (validates `%PDF` signature)
- Absolute URLs are built using `SITE_URL` for convenience in serializers

## CSV Import Format
Headers expected by `POST /upload-csv/`:
```
road_name,ward_number,location,length_km,width_m,road_type,material_type,road_category,area_name,district,state
```

## Development Tips
- Create an admin user with `createsuperuser` and browse `/admin/`.
- Ensure PostgreSQL is running and credentials match your `.env`.
- For emails via Gmail, use an App Password and enable SMTP.

## Running Tests
Add tests under each app’s `tests.py` and run:
```bash
python manage.py test
```

## License
Proprietary or to be specified by the project owners.

## Handover and Ownership
- Product: Suvidha Manch – Infrastructure Works Tracking Backend
- Code ownership: To be assumed by the receiving organisation
- Primary contacts: <to be filled by organisation>
- Environments: Development, Staging (optional), Production
- Source of truth for configuration: `.env` files per environment (keep secrets out of VCS)

## Production Deployment Guide
This project is WSGI-based (see `backend/wsgi.py`). Recommended stack: Gunicorn + Nginx + PostgreSQL on Linux. Daphne/Uvicorn can be used for ASGI if needed.

1) System prerequisites
- Python 3.11+
- PostgreSQL 13+
- Nginx (or any reverse proxy)
- Systemd for process management

2) Prepare application
```bash
# Clone and enter project
git clone <repo-url>
cd backend

# Create virtualenv
python -m venv .venv
source .venv/bin/activate

# Install deps
pip install --upgrade pip
pip install -r requirements.txt

# Create .env (see template above); ensure DEBUG=False, ALLOWED_HOSTS set

# Apply migrations
python manage.py migrate

# Create admin
python manage.py createsuperuser

# Ensure media directory exists and is writable
mkdir -p media
```

3) Run with Gunicorn (example)
```bash
pip install gunicorn
# Simple foreground run for smoke test
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

4) Systemd service (example)
```
[Unit]
Description=Suvidha Manch Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/suvidha/backend
Environment="PATH=/opt/suvidha/backend/.venv/bin"
EnvironmentFile=/opt/suvidha/backend/.env
ExecStart=/opt/suvidha/backend/.venv/bin/gunicorn backend.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

5) Nginx site (example)
```
server {
    listen 80;
    server_name your.domain;

    location /media/ {
        alias /opt/suvidha/backend/media/;
    }

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

Notes:
- Serve `media/` directly via Nginx. Keep it on persistent storage.
- HTTPS with Let’s Encrypt is recommended.

## Database and Media Backups
- PostgreSQL backup (daily recommended):
```bash
# Dump
pg_dump -h $DB_HOST -U $DB_USER -Fc $DB_NAME > suvidha_$(date +%F).dump
# Restore
pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME --clean suvidha_YYYY-MM-DD.dump
```
- Media backup: archive the `media/` directory (images and PDFs). Ensure the restore preserves paths: `media/infra_images/`, `media/infra_pdfs/`, `media/other_department_pdfs/`.

## Maintenance Runbook
- Migrations: `python manage.py makemigrations` then `python manage.py migrate`
- Creating users: via `/admin/` or `POST /accounts/register/`
- Resetting passwords: use `/accounts/request-password-reset/` flow or admin portal
- Rotating JWT settings: update related `SIMPLE_JWT_*` envs and restart app
- Email templates: update `EMAIL_TEMPLATE_FOR_STATUS_EMAIL`, `EMAIL_TEMPLATE_FOR_NEW_REQUEST`, `WELCOME_EMAIL_TEMPLATE` in environment; app reads them at runtime
- Data imports: use `POST /upload-csv/` with the documented headers
- Logs: configure systemd journal or reverse proxy logs; optional Sentry can be added

## Security Checklist (Production)
- DEBUG=False
- `ALLOWED_HOSTS` set to your domains
- Strong `SECRET_KEY` stored only in server secrets manager or `.env` not committed
- Enforce HTTPS at the proxy (HSTS recommended)
- Database: strong credentials, network restricted to app host
- JWT lifetimes appropriate to policy; consider short access tokens and longer refresh
- Admin access limited to trusted users; enable 2FA on email provider used for SMTP
- File uploads: images and PDFs only; validated server-side; store outside repo on persistent storage
- Regular backups and restore drills

## Observability
- Health check: add a lightweight endpoint or use `/admin/login/` reachability
- Metrics and error tracking: integrate tools like Sentry/Prometheus if required

## Versioning and Changes
- Python dependencies are pinned in `requirements.txt`
- Use git tags/releases for deployment snapshots
- Database schema tracked via Django migrations in each app’s `migrations/`

## Handover Notes
- Admin URL: `/admin/`
- Default modules and responsibilities:
  - `accounts/`: auth, JWT, password reset, emails
  - `core/`: core domain CRUD and CSV import, email utilities
  - `audit/`: audit logs and reporting API
- No cron jobs are required currently. Signals update infra work progress on `Update` creation.

