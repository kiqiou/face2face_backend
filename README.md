# Face2Face Backend

Backend part of a fullstack SPA application for online cosmetology booking system.

The project is built with Django REST Framework and provides a scalable API for managing users, bookings, procedures, schedules and Telegram-based authentication.

---

# Tech Stack

* Python 3
* Django
* Django REST Framework
* PostgreSQL
* Redis
* Docker / Docker Compose
* Telegram Bot API
* JWT Authentication

---

# Project Overview

Face2Face Backend is a REST API system that supports a role-based booking platform for cosmetology services.

The system is split into multiple Django applications responsible for different business domains:

* user management;
* booking system;
* procedures management;
* work schedule management;
* Telegram bot integration.

---

# Architecture

The project follows a modular Django architecture:

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

* user authentication
* role management
* Telegram ID binding
* user profiles

Key features:

* custom user model
* role-based access system
* JWT authentication support
* migrations for evolving user schema

---

### 2. Booking app

Core business logic of the system.

Responsible for:

* creating bookings
* managing appointment lifecycle
* calculating duration and price
* preventing schedule conflicts
* managing cosmetologist-client relations

Key components:

* models.py — booking entities
* serializers.py — API serialization
* views/ — REST endpoints
* utils.py — time slot generation logic
* migrations — complex schema evolution

---

### 3. Work day / schedule system

Responsible for:

* cosmetologist work schedule
* free interval calculation
* time slot generation
* booking validation

Features:

* dynamic schedule creation
* support for breaks
* conflict detection with existing bookings
* integration with booking duration logic

---

### 4. Procedure app

Responsible for:

* cosmetologist procedures
* pricing
* duration management
* procedure assignment to bookings

---

### 5. Telegram Bot integration (tg_bot)

Responsible for:

* user registration flow
* sending authentication codes
* linking Telegram accounts with users
* background message processing

Key components:

* handlers.py — bot logic
* signals.py — integration with Django events
* run_bot.py — bot runner
* management commands — startup automation

---

# Authentication system

The system uses hybrid authentication:

* Telegram-based verification for registration
* JWT tokens for API authentication
* Redis used for temporary storage of verification data

Flow:

1. User enters phone number
2. Telegram bot sends verification code
3. Code is validated via backend
4. JWT tokens are generated
5. User is authenticated in SPA frontend

---

# Booking system (core logic)

The most complex part of the system is the booking engine:

## Features:

* dynamic free time calculation
* procedure duration aggregation
* slot generation logic
* 5-minute interval segmentation
* conflict detection with existing bookings
* grouping time into logical intervals

This system ensures:

* no overlapping bookings
* accurate schedule management
* real-time availability calculation

---

# Database structure

Main entities:

* User
* Role
* Cosmetologist
* Procedure
* Booking
* WorkDay

Relationships:

* One-to-many (cosmetologist → procedures)
* Many-to-many (booking → procedures)
* One-to-one (user → role/profile)
* Temporal relations (workday ↔ booking conflicts)

---

# Docker setup

Project includes Docker support:

* docker-compose.yml for multi-service orchestration
* Dockerfile for backend containerization
* PostgreSQL + Redis integration

---

# API structure

Main API modules:

* /users/
* /booking/
* /procedures/
* /work-day/
* /telegram/

Each module contains:

* urls/
* views/
* serializers/

---

# Migrations

The project contains advanced migration history including:

* schema refactoring
* booking model evolution
* removal of legacy time-slot system
* addition of dynamic scheduling system
* Telegram integration fields

---

# Key technical challenges

## 1. Booking system logic

* dynamic slot generation
* overlapping prevention
* duration calculations

## 2. Telegram integration

* async communication between bot and backend
* secure code verification
* Redis-based temporary storage

## 3. Schedule management

* flexible workday creation
* break handling
* real-time validation

---

# Deployment

The project is containerized using Docker and can be deployed with:

```bash id="d1q9k2"
docker-compose up --build
```

---

# Author

Ekaterina Kuksar
GitHub: https://github.com/kiqiou
