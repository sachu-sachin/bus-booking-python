# 🚌 Bus Booking — Python CI/CD Demo

A production-style Python **bus booking system** demonstrating a full
**GitHub Actions CI/CD pipeline** with linting, multi-version testing,
type checking, security scanning, packaging, and deployment.

---

## 📁 Project Structure

```
bus-booking-python/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # ← GitHub Actions pipeline
├── app/
│   ├── __init__.py
│   ├── models.py              # Domain: Bus, Seat, Passenger, Booking
│   └── booking_service.py    # Service layer: search, book, cancel
├── tests/
│   ├── __init__.py
│   ├── test_models.py         # Unit tests for models
│   └── test_booking_service.py# Unit tests for service
├── .flake8
├── pyproject.toml             # pytest / black / isort / mypy config
├── requirements.txt
├── requirements-dev.txt
├── setup.cfg
└── setup.py
```

---

## ⚙️ GitHub Actions Pipeline Stages

| # | Job | Trigger | What it does |
|---|-----|---------|--------------|
| 1 | **Lint** | Every push / PR | Black format check, isort, flake8 |
| 2 | **Test** | After Lint | pytest + coverage on Python 3.10, 3.11, 3.12 |
| 3 | **Type Check** | After Lint | mypy static analysis |
| 4 | **Security** | After Lint | Bandit vulnerability scan |
| 5 | **Build** | After Test + Type + Security | Builds sdist & wheel |
| 6 | **Deploy** | Push to `main` only | Deploy to staging environment |

---

## 🚀 Quick Start (local)

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
pytest

# Format code
black .
isort .

# Lint
flake8 .

# Type check
mypy app/

# Security scan
bandit -r app/ -ll
```

---

## 🔑 Key Domain Concepts

- **Bus** — route, schedule, seat inventory, fare
- **Passenger** — with validation (name, email, phone, age)
- **Booking** — confirms a seat, generates a unique booking ID
- **BusBookingService** — orchestrates search → book → cancel flows

---

## 🏷️ Workflow Triggers

```yaml
on:
  push:
    branches: [ "main", "develop", "release/**" ]
  pull_request:
    branches: [ "main", "develop" ]
  workflow_dispatch:   # manual trigger from GitHub UI
```
