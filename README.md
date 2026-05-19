# SmartSave, Personal Finance Manager with Mobile Money Integration

> **Academic Project** – A mobile-first application that helps individuals manage personal finances, save via Mobile Money, and interact with multiple banks/microfinance institutions without complex bank APIs.

![License](https://img.shields.io/badge/license-MIT-blue)
![Django](https://img.shields.io/badge/Django-5.2-green);
![React Native](https://img.shields.io/badge/React%20Native-Expo-blue)

---

## Project Overview

SmartSave solves the **physical banking friction** in Cameroon (long queues, distance to branches, limited digital infrastructure). It allows users to:

- **Save money** via Mobile Money (MTN MoMo / Orange Money) without visiting a bank hall.
- **Request withdrawals** and track payout dates.
- **Manage expenses** (budgeting, categories, spending insights).
- **Link multiple banks or microfinance institutions** to one profile.
- **Receive SMS/email notifications** when deposits are confirmed or withdrawals are processed.

The system does **not** require real‑time bank APIs – it uses a **manual confirmation workflow** that mirrors how microfinance houses already operate with Mobile Money.

---

## Features

| Feature | Description |
|---------|-------------|
| 🔐 **User authentication** | Email/Password registration, JWT tokens (access + refresh). |
| 🏦 **Multiple institutions** | Users can add several banks / microfinance houses to their profile. |
| 💰 **Deposit via MoMo** | App displays institution's MoMo number → user sends money → enters transaction ID → bank admin confirms. |
| 💸 **Withdrawal request** | User requests cash → admin schedules payout → manual MoMo transfer → user notified. |
| 📊 **Expense tracking** | Log daily expenses with categories, amounts, dates, and notes. |
| 📈 **Spending summary** | View spending by category for day/week/month (mobile charts). |
| 🔔 **Notifications** | SMS (Twilio) and email (SMTP) alerts for confirmations and completions. |
| 🧑‍💼 **Bank dashboard** | Django admin panel for institutions to confirm deposits, schedule withdrawals, manage requests. |
| 📱 **Mobile app** | React Native / Expo app for iOS and Android. |

---

## 🏗️ Tech Stack

### Backend
- **Python 3.12+** / **Django 5.2** + **Django REST Framework**
- **PostgreSQL** (primary) / SQLite (development)
- **Celery** + **Redis** (async tasks – SMS/email)
- **JWT** (Simple JWT) + **djoser** (user registration)
- **Django Admin** (bank dashboard)
- **Gunicorn** + **Nginx** (production)

### Mobile App
- **React Native** (Expo SDK 50+)
- **Axios** (HTTP client)
- **React Navigation** (stack + bottom tabs)
- **AsyncStorage** / SecureStore (token storage)

### Infrastructure
- **Docker** + **Docker Compose** (all services)
- **Twilio** (SMS) – optional, can fallback to console
- **SMTP** (Gmail, SendGrid, etc.) – optional

---

## 📂 Project Structure

```
smart-save/
├── app/                         # Django backend
│   ├── finance_manager/         # Django project config
│   ├── apps/
│   │   ├── core/                # Shared base models
│   │   ├── users/               # Custom user + profile
│   │   ├── notifications/       # Email/SMS templates & sending
│   │   └── finance/             # Main finance logic
│   ├── static/                  # Static files
│   ├── media/                   # User uploads
│   ├── logs/                    # Application logs
│   ├── manage.py
│   └── requirements.txt
├── mobile/                      # React Native / Expo app
│   ├── App.js
│   ├── src/
│   │   ├── screens/             # Login, Dashboard, Deposit, Withdraw, Expenses
│   │   ├── components/          # Reusable UI
│   │   ├── services/            # API client (axios)
│   │   └── navigation/          # Stack & tab navigators
│   └── package.json
├── docker/
│   ├── local/
│   │   ├── django/Dockerfile
│   │   └── nginx/Dockerfile
│   └── production/
├── docker-compose.yml
├── .env.example
├── Makefile
├── about.md                     # Full project documentation (problem, solution)
├── architecture.md              # System architecture + ER diagrams
└── README.md                    # You are here
```

---

## Getting Started (Development)

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for mobile app)
- Expo Go app on your phone (or iOS/Android emulator)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/smart-save.git
cd smart-save
```

### 2. Backend Setup (Django)

#### Using Docker (recommended)
```bash
cp app/.env.example app/.env   # edit with your values
mkdir app/logs
touch app/logs/django.log      # Assuming Linux! look up for windows
docker-compose up -d --build
docker-compose exec api python manage.py migrate
docker-compose exec api python manage.py createsuperuser
```

The API will be available at `http://localhost:80/api/v1/`  
Django admin: `http://localhost:80/admin/`

#### Manual (without Docker)
```bash
cd app
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 3. Mobile App Setup (React Native / Expo)

```bash
cd mobile
npm install
npx expo start
```

Scan the QR code with Expo Go (Android) or Camera (iOS).

> **Note:** Update the API base URL in `mobile/src/services/api.js` to point to your backend (e.g., `http://192.168.x.x:80/api/v1`).

---

## Environment Variables (Backend)

Create a `.env` file inside `app/` (see `.env.example`).

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Set to `True` for development | `True` |
| `ALLOWED_HOSTS` | Comma-separated list | `localhost,127.0.0.1` |
| `POSTGRES_DB` | Database name | `smartsave` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `secret` |
| `REDIS_URL` | Redis connection | `redis://redis:6379/0` |
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL_HOST_USER` | SMTP username | `your@gmail.com` |
| `EMAIL_HOST_PASSWORD` | SMTP password | `app password` |
| `TWILIO_ACCOUNT_SID` | Twilio SID (optional) | `AC...` |
| `TWILIO_AUTH_TOKEN` | Twilio token (optional) | `...` |
| `TWILIO_PHONE_NUMBER` | Sender phone number | `+1234567890` |

> For development, SMS and email will be printed to console if not configured.

---

## API Endpoints (Main)

All endpoints require JWT token: `Authorization: Bearer <access_token>`

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|--------------|
| `GET` | `/api/v1/finance/institutions/` | List active banks/MFs | Authenticated user |
| `POST` | `/api/v1/finance/deposits/` | Create deposit request | User |
| `GET` | `/api/v1/finance/deposits/` | List user's deposits | User |
| `PATCH` | `/api/v1/finance/deposits/{id}/confirm/` | Confirm deposit | Bank admin |
| `POST` | `/api/v1/finance/withdrawals/` | Request withdrawal | User |
| `GET` | `/api/v1/finance/withdrawals/` | List user's withdrawals | User |
| `PATCH` | `/api/v1/finance/withdrawals/{id}/schedule/` | Set payout date | Bank admin |
| `PATCH` | `/api/v1/finance/withdrawals/{id}/complete/` | Complete withdrawal | Bank admin |
| `POST` | `/api/v1/finance/expenses/` | Add expense | User |
| `GET` | `/api/v1/finance/expenses/` | List expenses | User |
| `GET` | `/api/v1/finance/expenses/summary/?period=week` | Spending summary | User |

Full OpenAPI schema available at `/api/schema/` (drf-spectacular).

---

## Testing (Backend)

```bash
docker-compose exec api python manage.py test apps.finance
```

Or without Docker:
```bash
cd app
python manage.py test apps.finance
```

---

## Docker Services

| Service | Container name | Port (host) | Purpose |
|---------|----------------|-------------|---------|
| `nginx` | `smartsave-nginx` | 80, 443 | Reverse proxy, static/media |
| `api` | `smartsave-django` | - | Gunicorn + Django |
| `postgres-db` | `smartsave-postgres` | 5432 | PostgreSQL |
| `redis` | `smartsave-redis` | 6379 | Message broker |
| `celery_worker` | `smartsave-celery` | - | Async tasks |

Stop all: `docker-compose down`  
Rebuild: `docker-compose up --build`

---

## Roles & Permissions

| Role | Description |
|------|-------------|
| **User** | Can register, add institutions, deposit, withdraw, log expenses. |
| **Bank Admin** | Staff user linked to one `FinancialInstitution`. Can confirm deposits, schedule/complete withdrawals for that institution only. |
| **Superuser** | Full access to all institutions, manage users, etc. |

To create a bank admin:
```bash
docker-compose exec api python manage.py shell
```
```python
from apps.users.models import User
user = User.objects.create_user(email='admin@bank.com', username='bankadmin', first_name='Bank', last_name='Admin', password='securepass', is_staff=True)
from apps.finance.models import FinancialInstitution
inst = FinancialInstitution.objects.first()
user.profile.managed_institution = inst   # add a custom field (extend Profile)
user.save()
```

> See `apps/finance/permissions.py` for exact logic.

---

## Workflow Summary (Manual Confirmation)

1. **Deposit:** User sends MoMo → enters transaction ID → bank admin verifies and confirms.
2. **Withdrawal:** User requests withdrawal → admin sets payout date → after manual MoMo transfer, admin marks as completed.
3. **Expense:** User logs spending – no confirmation needed.

> No automatic bank API calls. This is intentional to match local infrastructure constraints.

---

## License

MIT License – free for educational and non‑commercial use.

---

## Additional Documentation

- [Project Description & Problem Statement](./docs/about.md)
- [System Architecture, ER Diagrams, State Machines](./docs/architecture.md)

---

*SmartSave – Making personal finance accessible to everyone, no bank queues required.*
