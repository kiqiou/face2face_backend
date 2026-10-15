# Face2Face Backend

Backend part of a fullstack application for an online cosmetics store with an integrated cosmetology booking system.

The project is built with Django REST Framework and provides a scalable API for managing a product catalog, orders, promotions, loyalty discounts, cosmetologist bookings, and Telegram-based authentication.

---

# Tech Stack

* Python 3
* Django / Django REST Framework
* PostgreSQL
* Redis
* Docker / Docker Compose
* Nginx
* Gunicorn
* Cloudinary (media storage)
* Telegram Bot API
* JWT Authentication

---

# Project Overview

Face2Face Backend started as a booking platform for cosmetology procedures and evolved into a hybrid system: an **online store** for cosmetic products, with the original **booking engine** kept alongside it for in-person procedures.

The system is split into multiple Django applications responsible for different business domains:

* user management and Telegram-based authentication
* product catalog (products, manufacturers, collections, skin types)
* order management (cart, checkout, promo codes, loyalty discounts)
* cosmetologist booking system (procedures, work schedules, appointments)

---

# Architecture

## Core project

```
face2face_back/
- settings.py
- urls.py
- asgi.py
- wsgi.py
```

Responsible for global configuration, routing and deployment setup.

---

## Main applications

### 1. Users app

Responsible for:

* custom user model
* Telegram ID binding
* JWT authentication support
* role-based access

---

### 2. Products / Catalog

Responsible for the product catalog and everything needed for regulatory-compliant product cards.

Key models:

* **Product** — name, pricing (`price_amount`, optional `sale_price` with an `effective_price` / `is_on_sale` property), manufacturer, in-stock status, Cloudinary image
* **ProductMedia** — multiple images/videos per product, ordered
* **Manufacturer** — including legal address and country of origin (required under TP TC 009/2011 art. 5.9.2)
* **Collection**, **SkinType**, **ProductPurpose** — catalog filtering/classification
* Compliance fields on `Product`: `net_amount`, `ingredients`, `shelf_life_months`, `storage_conditions`, `usage_instructions`, `conformity_document_number`, etc. — required disclosures for cosmetic products under technical regulation

---

### 3. Orders

Core e-commerce logic.

Key models:

* **Order** — status lifecycle (`new` → `confirmed` → `done` / `cancelled`), payment method (cash/card), approval method (call/message), linked promo code and discount
* **OrderItem** — snapshots `price_at_order` and `cost_price_at_order`, so historical orders stay accurate even if product prices change later; uses `PROTECT` on the product FK to prevent deleting a product that has order history
* **PromoCode** / **PromoCodeUsage** — percentage discounts, first-order-only flag, usage limits, validity windows, one-use-per-user enforcement
* **LoyaltyTier** — automatic discount tiers based on a customer's total historical spend

---

### 4. Booking system (cosmetology procedures)

Retained from the original platform for in-person appointments.

Key models:

* **Cosmetologist** — linked one-to-one to a `User`, with bio and specializations
* **Procedure** — name, price, duration, buffer time between appointments, tied to a cosmetologist
* **Booking** — links a user, cosmetologist and one or more procedures to a date/time slot
* **WorkDay** — defines a cosmetologist's working hours per date, including non-working days

Features:

* dynamic free time-slot calculation
* conflict detection against existing bookings
* duration aggregation across multiple procedures in one booking

---

### 5. Telegram Bot integration (tg_bot)

Responsible for:

* user registration flow
* sending authentication/verification codes
* linking Telegram accounts with users
* background message processing

Authentication flow:

1. User enters phone number
2. Telegram bot sends a verification code
3. Code is validated via the backend
4. JWT tokens are issued
5. User is authenticated in the SPA frontend

Redis is used for temporary storage of verification codes during this flow.

---

# Database structure (high level)

**Catalog:** `Product`, `Manufacturer`, `Collection`, `SkinType`, `ProductPurpose`, `ProductMedia`

**Commerce:** `Order`, `OrderItem`, `PromoCode`, `PromoCodeUsage`, `LoyaltyTier`

**Booking:** `Cosmetologist`, `Procedure`, `Booking`, `WorkDay`

**Users:** `User`

Notable relationships:

* `Product` → `Manufacturer` (many-to-one, `PROTECT`)
* `Product` ↔ `SkinType` / `ProductPurpose` / `Collection` (many-to-many)
* `Order` → `OrderItem` (one-to-many), prices snapshotted at order time
* `Booking` ↔ `Procedure` (many-to-many), `Booking` → `Cosmetologist` (many-to-one)
* `Cosmetologist` → `User` (one-to-one)

---

# Key technical challenges

## 1. Price integrity on orders

`OrderItem` stores `price_at_order` and `cost_price_at_order` as snapshots rather than referencing the live `Product` price — so historical orders remain accurate for accounting even after a product's price changes, while the FK to `Product` is `PROTECT`ed to preserve order history.

## 2. Promotions and loyalty logic

Promo codes support percentage discounts, first-order-only restrictions, usage caps and validity windows, enforced with a `unique_together` constraint so a code can only be used once per user. Loyalty discounts are tier-based on cumulative spend, calculated independently of promo codes.

## 3. Booking engine

Dynamic slot generation, buffer time between procedures, and conflict detection against a cosmetologist's `WorkDay` and existing `Booking` records.

## 4. Telegram-based auth

Async communication between the bot and the backend, with Redis as short-lived storage for verification codes rather than persisting them in the primary database.

## 5. Regulatory compliance

Product model carries the full set of disclosures required under TP TC 009/2011 (technical regulation on cosmetics/perfumery safety) — composition, shelf life, storage conditions, usage instructions and conformity document tracking.

---

# Deployment

The project is deployed with Docker Compose behind Nginx, serving both the API and the built Vue frontend from a single entry point.

## Services

| Service | Role |
|---|---|
| `web` | Django app, served via Gunicorn |
| `bot` | Telegram bot (registration/auth), separate process from `web` |
| `db` | PostgreSQL |
| `redis` | Verification code storage |
| `nginx` | Reverse proxy — routes `/api/` to `web`, serves the built frontend (`dist/`) at `/` |
| `pgadmin` | DB inspection, bound to `127.0.0.1` only (accessed via SSH tunnel, not exposed publicly) |

## Startup sequence

`web` depends on `db` with a `service_healthy` condition (via `pg_isready`), so migrations don't run before Postgres is actually ready to accept connections — important on a fresh volume, where Postgres needs time for first-time initialization.

On container start, `web` runs:

```bash
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn face2face_back.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## Environment variables

Configured via `.env` (not committed to the repository):

* `DJANGO_SECRET_KEY`, `DEBUG`, `DJANGO_ALLOWED_HOSTS`
* `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (consumed by Django) and the matching `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` (consumed by the `db` container)
* `REDIS_URL`
* `CLOUDINARY_URL`
* `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_NAME`, `ADMIN_TG_CHAT_ID`
* `PGADMIN_EMAIL`, `PGADMIN_PASSWORD`

## Networking

* Only `nginx` (ports 80/443) is exposed to the internet; `web` has no published port and is reachable only inside the Docker network, via `nginx`'s reverse proxy.
* `pgadmin` is bound to `127.0.0.1:6060`, accessible only through an SSH tunnel from an operator's machine.
* The frontend (Vue, built separately with `npm run build`) is mounted into the `nginx` container and served as static files; API calls use a relative `/api/` base URL so the same build works regardless of domain/IP.

## Running

```bash
docker compose up -d --build
docker compose ps
docker compose logs web
```

Static/media note: product images and media are stored on Cloudinary, not on the server's local filesystem — no local media volume or separate static-file serving config is needed for user-uploaded content.

---

# Author

Ekaterina Kuksar
GitHub: https://github.com/kiqiou
