# 🧠 ObjectVision Backend

<img src="https://object-vision-frontend.vercel.app/object-vision-logo.png" alt="ObjectVision Logo" width="200px" height="auto" />

Welcome to the **ObjectVision Backend** — the powerhouse behind the ObjectVision platform. Built with **FastAPI**, it supports secure and scalable object detection workflows, asynchronous tasks, email services, and more.

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.2-009688.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)

## 📑 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Authentication](#-authentication)
- [Database Management](#-database-management)
- [Running with Docker](#-running-with-docker)
- [Task Queue with Celery](#-task-queue-with-celery) 
- [Email Service](#-email-service)
- [Object Detection Pipeline](#-object-detection-pipeline)
- [Caching Strategy](#-caching-strategy)
- [Logging and Monitoring](#-logging-and-monitoring)
- [Running Tests](#-running-tests)
- [Performance Optimization](#-performance-optimization)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)
- [Contact](#-contact)

---

## ✨ Features

- 🔌 **FastAPI** for blazing-fast RESTful APIs with automatic OpenAPI documentation
- 🎯 **Celery** for robust asynchronous background task management
- ⚡️ **Redis** for high-performance caching and task queuing
- 🐘 **PostgreSQL** for reliable and scalable data storage
- 📧 **Brevo** integration for dynamic email services and notifications
- 🔐 **JWT Authentication** with token blacklisting and refresh mechanisms
- 🔄 **Alembic** for seamless database migrations
- 📊 **Pydantic** for data validation and settings management
- 🐳 **Dockerized** for effortless deployment and scaling
- 📝 **Comprehensive Logging** for monitoring and debugging
- 🧪 **Pytest** for extensive unit and integration testing
- 🔍 **OpenTelemetry** for distributed tracing and performance monitoring

---

## 🏗️ System Architecture

ObjectVision Backend follows a modern, scalable architecture designed for high performance and maintainability:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Client Apps    │◄────►│  Load Balancer  │◄────►│  FastAPI Servers│
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └────────┬────────┘
                                                           │
                                                           │
                     ┌──────────────────────────────────┐  │
                     │                                  │  │
                     │            Database              │◄-┘
                     │          (PostgreSQL)            │
                     │                                  │
                     └───────────────┬──────────────────┘
                                     │
                                     │
                     ┌───────────────▼──────────────────┐
                     │                                  │
                     │           Redis Cache            │
                     │                                  │
                     └───────────────┬──────────────────┘
                                     │
                                     │
┌─────────────────┐      ┌───────────▼──────────────────┐      ┌─────────────────┐
│                 │      │                              │      │                 │
│  ML Models      │◄────►│        Celery Workers        │◄────►│  Object Storage │
│                 │      │                              │      │                 │
└─────────────────┘      └──────────────────────────────┘      └─────────────────┘
```

This architecture ensures:
- **Horizontal Scalability**: Add more FastAPI servers or Celery workers as demand increases
- **High Availability**: Redundant components prevent single points of failure
- **Performance**: Asynchronous processing for compute-intensive tasks
- **Separation of Concerns**: Clear boundaries between application layers

---

## 📁 Project Structure

```bash
objectvision-backend/
├── app/
│   ├── configuration/      # App configuration and settings management
│   │   ├── config.py       # Environment-specific configurations
│   │   ├── redis-config.py # Application constants
│   │   └── yolo-config.py  # FastAPI dependencies
│   │
│   ├── db/                 # Database models and configuration
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── migrations/     # Alembic migration scripts
│   │   └── database.py     # Database connection and session management
│   │
│   ├── docs/               # API documentation and examples
│   │   ├── openapi.json    # Generated OpenAPI specification
│   │   └── examples/       # Request/response examples
│   │
│   ├── handlers/              # Exception & request handlers
│   │   ├── error_handler.py   # Global exception handlers
│   │   └── request_handler.py # Request preprocessing
│   │
│   ├── helpers/             # Helper functions and utilities
│   │   ├── auth_helpers.py  # Authentication helpers
│   │   ├── email_helpers.py # Email formatting helpers
│   │   └── image_helpers.py # Image processing utilities
│   │
│   ├── middleware/               # Custom middleware components
│   │   ├── auth_middleware.py    # Authentication middleware
│   │   ├── logging_middleware.py # Request logging
│   │   └── rate_limiter.py       # API rate limiting
│   │
│   ├── performance/         # Performance enhancements
│   │   ├── caching.py       # Cache implementations
│   │   └── optimizations.py # Performance optimizations
│   │
│   ├── repository/         # Database repository patterns
│   │   ├── base.py         # Base repository class
│   │   ├── user_repository.py # User-related database operations
│   │   └── detection_repository.py # Detection result storage
│   │
│   ├── routes/             # API route definitions
│   │   ├── api.py          # API router aggregation
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── users.py        # User management endpoints
│   │   └── detections.py   # Object detection endpoints
│   │
│   ├── schedulers/          # Scheduled background tasks
│   │   ├── cleanup_tasks.py # Data cleanup jobs
│   │   └── report_tasks.py  # Scheduled reports generation
│   │
│   ├── schemas/            # Pydantic schemas for validation
│   │   ├── auth.py         # Authentication schemas
│   │   ├── users.py        # User data schemas
│   │   └── detections.py   # Detection request/response schemas
│   │
│   ├── services/                # Business logic & external integrations
│   │   ├── auth_service.py      # Authentication service
│   │   ├── email_service.py     # Email service
│   │   ├── user_service.py      # User management service
│   │   └── detection_service.py # Object detection service
│   │
│   ├── tasks/                 # Celery task definitions
│   │   ├── celery_app.py      # Celery app configuration
│   │   ├── email_tasks.py     # Email sending tasks
│   │   └── detection_tasks.py # Object detection processing tasks
│   │
│   ├── templates/          # Jinja email templates
│   │   ├── base.html       # Base email template
│   │   ├── welcome.html    # Welcome email template
│   │   └── report.html     # Detection report template
│   │
│   ├── utils/              # Utility functions
│   │   ├── security.py     # Security utilities
│   │   ├── validators.py   # Custom validators
│   │   └── formatters.py   # Data formatters
│   │
│   └── main.py             # Application entry point
│
├── tests/                  # Test suite
│   ├── conftest.py         # Test configurations and fixtures
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
│
├── scripts/                # Utility scripts
│   ├── seed_db.py          # Database seeding script
│   └── generate_api_docs.py # API documentation generator
│
├── logs/                   # Log files directory
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore rules
├── alembic.ini             # Alembic configuration
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker build instructions
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── pytest.ini              # Pytest configuration
└── README.md               # This file
```

---

## 🔧 Prerequisites

Make sure you have the following installed:

- **Python 3.10+**: The core programming language
- **PostgreSQL 14+**: Primary database
- **Redis 6+**: Caching and task queue
- **Docker & Docker Compose**: For containerized deployment
- **Git**: Version control system

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/imtiaj-007/ObjectVision-Backend.git
cd objectvision-backend
```

### 2. Set Up a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# For development, include development tools
pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables

Create a `.env.development` file based on the provided example:

```env
# env type
ENVIRONMENT=development/staging/production
API_BASE_URL=http://localhost:8000

# Frontend URLs
FRONTEND_BASE_URL=http://localhost:3000
FRONTEND_SUCCESS_URL="http://localhost:3000/success"
FRONTEND_ERROR_URL="http://localhost:3000/error"

# Database Configuration
DB_HOST='your_postgres_host_name'
DB_USER='your_postgres_user_name'
DB_NAME='your_db_provider_name'
DB_PASSWORD='your_db_password'

# Redis Credentials
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/0

# Authentication
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Brevo Credentials
BREVO_API_URL=https://api.brevo.com/v3/smtp/email
BREVO_API_KEY=your_brevo_api_key
EMAIL_SENDER=your_email_id
EMAIL_SENDER_NAME="SK Imtiaj Uddin"
COMPANY_NAME=ObjectVision

# Machine Learning Model Configuration
MODEL_PATH=/path/to/ml/model
CONFIDENCE_THRESHOLD=0.5
```

Reference the `.env.example` file for all available configuration options.

### 5. Apply Database Migrations

```bash
# Initialize migrations if not already done
alembic init migrations

# Create a new migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 6. Start the Development Server

```bash
# Start the server with hot-reloading
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

This will launch the API server at [http://localhost:8000](http://localhost:8000)

---

## 🔐 Environment Variables

ObjectVision Backend uses environment variables for configuration. Here's a detailed breakdown of all supported keys:

### Application Settings
| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Application environment | `development`, `staging`, `production` |
| `API_BASE_URL` | Base URL for backend API | `http://localhost:8000` |

### Frontend URLs
| Variable | Description | Example |
|----------|-------------|---------|
| `FRONTEND_BASE_URL` | Base URL for frontend | `http://localhost:3000` |
| `FRONTEND_SUCCESS_URL` | Redirect URL after success | `http://localhost:3000/success` |
| `FRONTEND_ERROR_URL` | Redirect URL after error | `http://localhost:3000/error` |

### Database Configuration
| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_USER` | PostgreSQL user | `postgres` |
| `DB_NAME` | Database name | `objectvision` |
| `DB_PASSWORD` | Database password | `yourpassword` |

### Redis Configuration
| Variable | Description | Example |
|----------|-------------|---------|
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |

### Authentication
| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | JWT signing key | `jwtsecretkey123!` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime in days | `7` |

### Email Service (Brevo)
| Variable | Description | Example |
|----------|-------------|---------|
| `BREVO_API_URL` | Brevo API endpoint | `https://api.brevo.com/v3/smtp/email` |
| `BREVO_API_KEY` | Brevo API key | `your_brevo_api_key` |
| `EMAIL_SENDER` | Email address used to send messages | `noreply@example.com` |
| `EMAIL_SENDER_NAME` | Display name for email sender | `SK Imtiaj Uddin` |
| `COMPANY_NAME` | Name used in email templates | `ObjectVision` |

### Object Detection Configuration
| Variable | Description | Example |
|----------|-------------|---------|
| `MODEL_PATH` | Path to machine learning model | `/path/to/ml/model` |
| `CONFIDENCE_THRESHOLD` | Detection confidence threshold | `0.5` |

---

## 📚 API Documentation

ObjectVision Backend automatically generates comprehensive API documentation:

### Interactive Documentation
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Interactive API explorer
  - Try API endpoints directly from the browser
  - Authentication built-in

- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
  - Alternative documentation viewer
  - Clean, responsive interface
  - Better for complex schema documentation

### API Endpoints Overview

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|---------------|
| `/api/v1/auth/signup` | POST | Register a new user | Public |
| `/api/v1/auth/login` | POST | Authenticate user | Public |
| `/api/v1/auth/refresh` | POST | Refresh access token | Public |
| `/api/v1/auth/logout` | POST | Log out (blacklist token) | JWT |
| `/api/v1/users/get-profile` | GET | Get current user profile | JWT |
| `/api/v1/users/{user_id}` | GET | Get user by ID | JWT |
| `/api/v1/users/{user_id}` | PATCH | Update user profile | JWT |
| `/api/v1/detect/image` | POST | Process single image | JWT |
| `/api/v1/detect/batch` | POST | Process multiple images | JWT |
| `/api/v1/detect/jobs/{job_id}` | GET | Get detection job status | JWT |
| `/api/v1/detect/history` | GET | Get detection history | JWT |

### API Versioning

The API uses URL-based versioning (`/api/v1/`) to ensure backward compatibility as the API evolves. Future versions (v2, v3) can be implemented alongside existing versions without breaking client applications.

---

## 🔒 Authentication

ObjectVision Backend implements a secure JWT-based authentication system:

### Authentication Flow

1. **Registration**:
   - Client submits email, password, and profile info
   - Backend validates data and creates a new user
   - Welcome email is sent asynchronously via Celery

2. **Login**:
   - Client submits email and password
   - Backend verifies credentials
   - If valid, returns an access token (short-lived) and refresh token (long-lived)

3. **Authorized Requests**:
   - Client includes access token in `Authorization: Bearer {token}` header
   - Backend validates token signature and expiration
   - If valid, the request proceeds

4. **Token Refresh**:
   - When access token expires, client uses refresh token to get a new access token
   - This prevents frequent re-authentication

5. **Logout**:
   - Client submits refresh token
   - Backend adds token to blacklist in Redis
   - Future requests with that token will be rejected

### Security Measures

- **Password Hashing**: Argon2id for secure password storage
- **Token Blacklisting**: Prevents token reuse after logout
- **Rate Limiting**: Prevents brute force attacks
- **CORS Protection**: Restricts API access to allowed origins
- **Token Expiration**: Short-lived access tokens limit damage from token theft

---

## 📊 Database Management

ObjectVision Backend uses PostgreSQL with SQLAlchemy ORM for data management:

### Entity Relationship Diagram

```
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│    Users      │       │   Detections  │       │DetectionResults
├───────────────┤       ├───────────────┤       ├───────────────┤
│id: UUID       │       │id: UUID       │       │id: UUID       │
│email: String  │       │user_id: UUID  │───┐   │detection_id:UUID
│password: String       │name: String   │   │   │object_class:String
│name: String   │       │status: String │   └──►│confidence: Float
│created_at: Date       │created_at: Date       │bbox_x: Float   │
│updated_at: Date       │updated_at: Date       │bbox_y: Float   │
└───────────────┘       └───────────────┘       │bbox_width: Float
        │                       │               │bbox_height:Float
        │                       │               └───────────────┘
        │                       │
        │                       │
        ▼                       ▼
┌───────────────┐       ┌───────────────┐
│  UserSettings │       │DetectionImages│
├───────────────┤       ├───────────────┤
│user_id: UUID  │       │id: UUID       │
│theme: String  │       │detection_id:UUID
│notifications: Bool    │image_path:String
│api_key: String│       │processed: Bool 
└───────────────┘       └───────────────┘
```

### Migrations with Alembic

Alembic handles database schema migrations:

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "Add new field to users"

# Apply pending migrations
alembic upgrade head

# Rollback the last migration
alembic downgrade -1

# View migration history
alembic history --verbose
```

### Database Optimization

- **Connection Pooling**: Efficiently reuses database connections
- **Indexes**: Strategic indexes on frequently queried columns
- **Pagination**: All list endpoints support pagination to limit query size
- **Query Optimization**: Eager loading of related objects to prevent N+1 queries

---

## 🐳 Running with Docker

ObjectVision Backend includes full Docker support for development and production:

### Docker Compose Setup

```bash
# Start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
```

This will create and start:

- ✅ **FastAPI App**: Running on `localhost:8000`
- 🔁 **Redis**: Cache and message broker on `localhost:6379`
- 👷 **Celery Worker**: Processing background tasks
- 🌸 **Flower**: Celery monitoring on `localhost:5555`

### Docker for Production

For production deployment, a multi-stage Dockerfile is provided:

```Dockerfile
# Build stage
FROM python:3.10-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.10-slim

WORKDIR /app
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser

CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "4"]
```

This approach:
- Minimizes image size
- Improves security by using a non-root user
- Optimizes build caching
- Uses Gunicorn with Uvicorn workers for production-ready serving

---

## ⚙️ Task Queue with Celery

ObjectVision Backend leverages Celery for asynchronous task processing:

### Celery Configuration

```python
# app/tasks/celery_app.py
from celery import Celery
from app.configuration.config import settings

celery_app = Celery(
    "objectvision",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.detection_tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    worker_max_tasks_per_child=200,
    broker_connection_retry_on_startup=True,
)
```

### Running Celery

```bash
# Start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# Start Celery worker with concurrency
celery -A app.tasks.celery_app worker --concurrency=4 --loglevel=info

# Start Celery beat for scheduled tasks
celery -A app.tasks.celery_app beat --loglevel=info

# Start Flower monitoring
celery -A app.tasks.celery_app flower --port=5555
```

### Example Task

```python
# app/tasks/detection_tasks.py
from app.tasks.celery_app import celery_app
from app.services.detection_service import detect_objects_in_image
import time

@celery_app.task(bind=True, name="process_image")
def process_image_task(self, image_path, user_id, detection_id, parameters):
    """
    Process an image for object detection as a background task.
    
    Args:
        image_path: Path to the uploaded image
        user_id: ID of the requesting user
        detection_id: ID of the detection job
        parameters: Detection parameters (confidence, etc.)
        
    Returns:
        dict: Detection results
    """
    # Update task status
    self.update_state(state="PROCESSING")
    
    # Perform detection
    try:
        results = detect_objects_in_image(image_path, parameters)
        
        # Save results to database
        save_detection_results(detection_id, results)
        
        return {
            "status": "completed",
            "detection_id": detection_id,
            "object_count": len(results)
        }
        
    except Exception as e:
        # Handle error
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise
```

---

## 📧 Email Service

ObjectVision Backend integrates with Brevo (formerly Sendinblue) for email notifications:

### Email Service Implementation

```python
# app/services/email_service.py
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from app.configuration.config import settings

class EmailService:
    def __init__(self):
        self.configuration = sib_api_v3_sdk.Configuration()
        self.configuration.api_key['api-key'] = settings.BREVO_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(self.configuration)
        )
        
    def send_email(self, to_email, to_name, subject, html_content, template_id=None):
        """Send an email using Brevo API"""
        sender = {"name": settings.EMAIL_FROM_NAME, "email": settings.EMAIL_FROM_ADDRESS}
        to = [{"email": to_email, "name": to_name}]
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            sender=sender,
            subject=subject,
            html_content=html_content,
            template_id=template_id
        )
        
        try:
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            return api_response
        except ApiException as e:
            # Log the error
            logger.error(f"Email API exception: {e}")
            raise
```

### Email Templates

The backend uses Jinja2 templates for consistent email formatting:

```html
<!-- app/templates/welcome.html -->
{% extends "base.html" %}

{% block content %}
<h1>Welcome to ObjectVision!</h1>
<p>Hello {{ name }},</p>
<p>Thank you for joining ObjectVision. We're excited to have you onboard!</p>
<p>Get started by uploading your first image for object detection.</p>
<a href="{{ dashboard_url }}" class="button">Go to Dashboard</a>
{% endblock %}
```

### Asynchronous Email Delivery

Emails are sent asynchronously via Celery to prevent API request blocking:

```python
# app/tasks/email_tasks.py
from app.tasks.celery_app import celery_app
from app.services.email_service import EmailService
from jinja2 import Environment, FileSystemLoader
import os

@celery_app.task(name="send_welcome_email")
def send_welcome_email(user_email, user_name):
    """Send welcome email to newly registered users"""
    # Setup template environment
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("welcome.html")
    
    # Render HTML content
    dashboard_url = f"{settings.FRONTEND_URL}/dashboard"
    html_content = template.render(name=user_name, dashboard_url=dashboard_url)
    
    # Send email
    email_service = EmailService()
    return email_service.send_email(
        to_email=user_email,
        to_name=user_name,
        subject="Welcome to ObjectVision!",
        html_content=html_content
    )
```

---

## 🔎 Object Detection Pipeline

ObjectVision Backend implements a comprehensive object detection pipeline powered by modern deep learning models:

### Detection Architecture

The detection pipeline utilizes a multi-stage approach:

1. **Image Pre-processing**:
   - Normalization and resizing
   - Format conversion for model compatibility
   - Optional augmentation for edge cases

2. **Model Inference**:
   - YOLOv8 model for real-time object detection
   - Configurable confidence threshold via environment variables
   - Multi-threading for parallel processing of batch uploads

3. **Post-processing**:
   - Non-maximum suppression to eliminate duplicate detections
   - Class filtering based on user preferences
   - Bounding box coordinate normalization

4. **Result Handling**:
   - Database storage of detection results
   - Optional annotated image generation
   - WebSocket notification of completion

### Implementation

```python
# app/services/detection_service.py
import cv2
import numpy as np
import torch
from app.configuration.config import settings
from app.configuration.yolo_config import get_model

class DetectionService:
    def __init__(self):
        self.model = get_model()
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        
    async def detect_objects(self, image_path, parameters=None):
        """
        Detect objects in an image using YOLO model
        
        Args:
            image_path: Path to input image
            parameters: Optional detection parameters
            
        Returns:
            List of detection results with class, confidence and coordinates
        """
        # Load and preprocess image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image at {image_path}")
            
        # Run inference
        results = self.model(image)
        
        # Process results
        detections = []
        for detection in results.xyxy[0]:
            x1, y1, x2, y2, confidence, class_id = detection
            
            if confidence < self.confidence_threshold:
                continue
                
            class_name = self.model.names[int(class_id)]
            
            detections.append({
                "class": class_name,
                "confidence": float(confidence),
                "bbox": {
                    "x1": float(x1),
                    "y1": float(y1),
                    "x2": float(x2),
                    "y2": float(y2),
                    "width": float(x2 - x1),
                    "height": float(y2 - y1)
                }
            })
            
        return detections
```

---

## 📊 Caching Strategy

ObjectVision Backend implements a multi-level caching strategy to optimize performance and reduce database load:

### Redis Cache Implementation

```python
# app/performance/caching.py
from redis import Redis
from app.configuration.config import settings
import json
import pickle

class RedisCache:
    def __init__(self):
        self.redis_client = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,  # For string data
            socket_timeout=5
        )
        self.binary_redis = Redis.from_url(  # For binary data
            settings.REDIS_URL,
            decode_responses=False,
            socket_timeout=5
        )
        
    def get(self, key, default=None):
        """Get a string value from cache"""
        value = self.redis_client.get(key)
        return value if value is not None else default
        
    def set(self, key, value, expire=3600):
        """Set a string value in cache with expiration"""
        return self.redis_client.set(key, value, ex=expire)
        
    def get_json(self, key, default=None):
        """Get and deserialize JSON data"""
        value = self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return default
        
    def set_json(self, key, value, expire=3600):
        """Serialize and store JSON data"""
        json_value = json.dumps(value)
        return self.set(key, json_value, expire)
        
    def get_object(self, key, default=None):
        """Get and unpickle Python object"""
        value = self.binary_redis.get(key)
        if value:
            try:
                return pickle.loads(value)
            except:
                pass
        return default
        
    def set_object(self, key, value, expire=3600):
        """Pickle and store Python object"""
        pickled_value = pickle.dumps(value)
        return self.binary_redis.set(key, pickled_value, ex=expire)
        
    def delete(self, key):
        """Remove a key from cache"""
        return self.redis_client.delete(key)
```

### Caching Strategy Tiers

1. **Route-Level Cache**: Fast responses for frequently accessed, read-heavy endpoints
   - User profile data: 15-minute TTL
   - Public detection results: 1-hour TTL
   - API documentation: 24-hour TTL

2. **Query-Level Cache**: Database query result caching
   - Detection history queries: 5-minute TTL
   - User statistics: 10-minute TTL

3. **Object-Level Cache**: Individual business objects
   - User settings: 30-minute TTL
   - Detection job status: 1-minute TTL (frequently updated)

4. **Token Blacklist**: JWT security with automatic expiration
   - Invalidated tokens: TTL matches token expiration time

### Cache Invalidation Strategy

- **User Profile Update**: Instantly invalidates user cache
- **Detection Job Status Change**: Invalidates related job caches
- **Database Writes**: Strategic cache clearing on DB changes

---

## 📝 Logging and Monitoring

ObjectVision Backend implements comprehensive logging and monitoring for reliability and performance insights:

### Structured Logging

```python
# app/middleware/logging_middleware.py
import time
import uuid
from fastapi import Request
import structlog
from app.configuration.config import settings

logger = structlog.get_logger()

async def logging_middleware(request: Request, call_next):
    """Middleware for request/response logging with timing and correlation IDs"""
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Start timer
    start_time = time.time()
    
    # Log request
    logger.info(
        "request_started",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        environment=settings.ENVIRONMENT
    )
    
    # Process request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            "request_completed",
            request_id=request_id,
            status_code=response.status_code,
            process_time_ms=round(process_time * 1000, 2),
            environment=settings.ENVIRONMENT
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        
        # Log error
        logger.error(
            "request_failed",
            request_id=request_id,
            error=str(e),
            process_time_ms=round(process_time * 1000, 2),
            environment=settings.ENVIRONMENT,
            exc_info=True
        )
        
        raise
```

### OpenTelemetry Integration

```python
# app/main.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def setup_telemetry(app):
    """Configure OpenTelemetry tracing for the application"""
    # Set up resource
    resource = Resource.create({"service.name": "objectvision-backend"})
    
    # Set up tracer provider
    tracer_provider = TracerProvider(resource=resource)
    
    # Configure exporter
    otlp_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
```

### Health Check Endpoints

```python
# app/routes/health.py
from fastapi import APIRouter, Depends
from app.db.database import get_db
from app.tasks.celery_app import celery_app
from redis import Redis
from app.configuration.config import settings

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint for monitoring and load balancers
    """
    return {"status": "ok", "service": "objectvision-api"}
    
@router.get("/health/database", tags=["Health"])
async def database_health(db = Depends(get_db)):
    """
    Database connectivity health check
    """
    try:
        # Execute simple query
        result = db.execute("SELECT 1").fetchone()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
@router.get("/health/redis", tags=["Health"])
async def redis_health():
    """
    Redis connectivity health check
    """
    try:
        redis = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        response = redis.ping()
        return {"status": "ok", "redis": "connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
@router.get("/health/celery", tags=["Health"])
async def celery_health():
    """
    Celery worker health check
    """
    try:
        i = celery_app.control.inspect()
        response = i.stats()
        if response:
            return {"status": "ok", "workers": list(response.keys())}
        return {"status": "error", "message": "No active workers found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

## 🧪 Running Tests

ObjectVision Backend uses pytest for comprehensive test coverage:

### Test Configuration

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.db.models.user import User
import os
import jwt
from datetime import datetime, timedelta
from app.configuration.config import settings

# Create test database
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_objectvision"

engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create fresh database tables for each test"""
    Base.metadata.create_all(bind=engine)
    
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Create test client with database dependency override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}

@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User(
        email="testuser@example.com",
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$random_hash",
        name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Generate authorization headers for the test user"""
    access_token = jwt.encode(
        {
            "sub": str(test_user.id),
            "exp": datetime.utcnow() + timedelta(minutes=30)
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return {"Authorization": f"Bearer {access_token}"}
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_auth.py

# Run with verbose output
pytest -v

# Show print statements during test
pytest -s
```

### Example Tests

```python
# tests/unit/test_auth.py
def test_register_user(client):
    """Test user registration endpoint"""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "newuser@example.com"
    assert "password" not in data

def test_login_user(client, test_user):
    """Test user login endpoint"""
    # Patch the password verification for testing
    from app.services.auth_service import verify_password as original_verify
    import app.services.auth_service
    
    # Mock verification to always return True for test
    app.services.auth_service.verify_password = lambda plain, hashed: True
    
    try:
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser@example.com",
                "password": "password"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    finally:
        # Restore original function
        app.services.auth_service.verify_password = original_verify
```

---

## ⚡ Performance Optimization

ObjectVision Backend incorporates multiple performance optimizations to ensure efficient operation even under high load:

### Database Optimization

1. **Connection Pooling**:
   ```python
   # app/db/database.py
   from sqlalchemy import create_engine
   from sqlalchemy.ext.declarative import declarative_base
   from sqlalchemy.orm import sessionmaker
   from app.configuration.config import settings
   
   engine = create_engine(
       settings.DATABASE_URL,
       pool_size=20,                # Maximum connections in pool
       max_overflow=10,             # Maximum overflow connections
       pool_timeout=30,             # Connection timeout in seconds
       pool_recycle=1800,           # Recycle connections after 30 minutes
       pool_pre_ping=True           # Verify connection validity before use
   )
   ```

2. **Strategic Indexing**:
   ```python
   # app/db/models/detection.py
   from sqlalchemy import Column, ForeignKey, String, DateTime, Index
   from sqlalchemy.dialects.postgresql import UUID
   from sqlalchemy.sql import func
   from app.db.database import Base
   import uuid
   
   class Detection(Base):
       __tablename__ = "detections"
       
       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
       user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
       status = Column(String, nullable=False)
       created_at = Column(DateTime(timezone=True), server_default=func.now())
       updated_at = Column(DateTime(timezone=True), onupdate=func.now())
       
       # Optimized indexes for common queries
       __table_args__ = (
           Index('idx_detection_user_id', user_id),
           Index('idx_detection_status', status),
           Index('idx_detection_created_at', created_at),
       )
   ```

3. **Query Optimization**:
   ```python
   # app/repository/detection_repository.py
   from sqlalchemy.orm import Session, joinedload
   from app.db.models.detection import Detection
   from app.db.models.detection_result import DetectionResult
   
   class DetectionRepository:
       def get_detections_with_results(self, db: Session, user_id: str, limit: int = 10, offset: int = 0):
           """
           Get user detections with eager loading of results to prevent N+1 query problems
           """
           return db.query(Detection)\
               .filter(Detection.user_id == user_id)\
               .options(joinedload(Detection.results))\
               .order_by(Detection.created_at.desc())\
               .limit(limit)\
               .offset(offset)\
               .all()
   ```

### API Optimization

1. **Response Compression**:
   ```python
   # app/main.py
   from fastapi.middleware.gzip import GZipMiddleware
   
   # Add compression middleware
   app.add_middleware(GZipMiddleware, minimum_size=1000)
   ```

2. **Pagination**:
   ```python
   # app/routes/detections.py
   from fastapi import APIRouter, Depends, Query
   
   @router.get("/history")
   async def get_detection_history(
       user_id: str = Depends(get_current_user_id),
       limit: int = Query(default=10, ge=1, le=100),
       offset: int = Query(default=0, ge=0),
       db: Session = Depends(get_db)
   ):
       """Get paginated detection history for a user"""
       repository = DetectionRepository()
       detections = repository.get_user_detections(db, user_id, limit, offset)
       total = repository.count_user_detections(db, user_id)
       
       return {
           "items": detections,
           "total": total,
           "limit": limit,
           "offset": offset
       }
   ```

3. **Async Handlers**:
   ```python
   # app/routes/detections.py
   @router.post("/image")
   async def detect_objects_in_image(
       image: UploadFile = File(...),
       current_user: str = Depends(get_current_user_id),
       db: Session = Depends(get_db)
   ):
       """
       Process image for object detection asynchronously
       """
       # Save uploaded file
       file_path = await save_upload_file(image)
       
       # Create detection record
       detection_service = DetectionService(db)
       detection_id = detection_service.create_detection_job(current_user)
       
       # Process asynchronously
       process_image_task.delay(file_path, current_user, detection_id)
       
       return {"detection_id": detection_id, "status": "processing"}
   ```

### Memory Optimization

1. **Streaming Responses**:
   ```python
   # app/routes/detections.py
   from fastapi.responses import StreamingResponse
   import io
   
   @router.get("/{detection_id}/image")
   async def get_annotated_image(
       detection_id: str,
       current_user: str = Depends(get_current_user_id),
       db: Session = Depends(get_db)
   ):
       """Stream annotated image instead of loading it entirely in memory"""
       # Get image path
       detection = get_detection_by_id(db, detection_id, current_user)
       image_path = detection.image_path
       
       # Open file as stream
       file_like = open(image_path, mode="rb")
       
       return StreamingResponse(
           file_like, 
           media_type="image/jpeg",
           headers={"Content-Disposition": f"inline; filename={detection_id}.jpg"}
       )
   ```

2. **Batch Processing**:
   ```python
   # app/repository/base.py
   from sqlalchemy.orm import Session
   
   class BaseRepository:
       def bulk_insert(self, db: Session, objects, batch_size=1000):
           """Insert records in batches to reduce memory usage"""
           for i in range(0, len(objects), batch_size):
               batch = objects[i:i+batch_size]
               db.bulk_save_objects(batch)
               db.flush()
   ```

---

## 🚀 Deployment

ObjectVision Backend supports multiple deployment options for different environments:

### Production Deployment Options

1. **Docker Swarm**:
   ```yaml
   # docker-stack.yml
   version: '3.8'
   
   services:
     api:
       image: objectvision/backend:latest
       environment:
         - ENVIRONMENT=production
         - DB_HOST=db
         - REDIS_HOST=redis
       deploy:
         replicas: 3
         update_config:
           parallelism: 1
           delay: 10s
         restart_policy:
           condition: on-failure
       ports:
         - "8000:8000"
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
       networks:
         - objectvision-network
   
     worker:
       image: objectvision/backend:latest
       command: celery -A app.tasks.celery_app worker --loglevel=info
       environment:
         - ENVIRONMENT=production
         - DB_HOST=db
         - REDIS_HOST=redis
       deploy:
         replicas: 2
         restart_policy:
           condition: on-failure
       networks:
         - objectvision-network
   
     db:
       image: postgres:14
       volumes:
         - postgres-data:/var/lib/postgresql/data
       environment:
         - POSTGRES_PASSWORD=securepassword
         - POSTGRES_USER=objectvision
         - POSTGRES_DB=objectvision
       deploy:
         placement:
           constraints: [node.role == manager]
       networks:
         - objectvision-network
   
     redis:
       image: redis:6
       volumes:
         - redis-data:/data
       deploy:
         placement:
           constraints: [node.role == manager]
       networks:
         - objectvision-network
   
   volumes:
     postgres-data:
     redis-data:
   
   networks:
     objectvision-network:
       driver: overlay
   ```

2. **Kubernetes Deployment**:
   ```yaml
   # kubernetes/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: objectvision-api
     labels:
       app: objectvision
       tier: backend
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: objectvision
         tier: backend
     template:
       metadata:
         labels:
           app: objectvision
           tier: backend
       spec:
         containers:
         - name: api
           image: objectvision/backend:latest
           ports:
           - containerPort: 8000
           env:
           - name: ENVIRONMENT
             value: "production"
           - name: DB_HOST
             value: "postgres-service"
           - name: REDIS_HOST
             value: "redis-service"
           livenessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 5
           resources:
             limits:
               cpu: "1"
               memory: "1Gi"
             requests:
               cpu: "500m"
               memory: "512Mi"
   ```

3. **CI/CD Pipeline**:
   ```yaml
   # .github/workflows/deploy.yml
   name: Deploy ObjectVision Backend
   
   on:
     push:
       branches: [main]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       services:
         postgres:
           image: postgres:14
           env:
             POSTGRES_PASSWORD: postgres
             POSTGRES_USER: postgres
             POSTGRES_DB: test_objectvision
           ports:
             - 5432:5432
         redis:
           image: redis:6
           ports:
             - 6379:6379
       steps:
         - uses: actions/checkout@v2
         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: 3.10
         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements-dev.txt
         - name: Run tests
           run: |
             pytest
     
     build:
       needs: test
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Login to Docker Hub
           uses: docker/login-action@v1
           with:
             username: ${{ secrets.DOCKER_HUB_USERNAME }}
             password: ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}
         - name: Build and push
           uses: docker/build-push-action@v2
           with:
             push: true
             tags: objectvision/backend:latest
     
     deploy:
       needs: build
       runs-on: ubuntu-latest
       steps:
         - name: Deploy to production server
           uses: appleboy/ssh-action@master
           with:
             host: ${{ secrets.SSH_HOST }}
             username: ${{ secrets.SSH_USERNAME }}
             key: ${{ secrets.SSH_PRIVATE_KEY }}
             script: |
               cd /opt/objectvision
               docker-compose pull
               docker-compose up -d
   ```

### Deployment Best Practices

1. **Database Migration Strategy**:
   - Use Alembic migrations with proper versioning
   - Apply migrations before deploying new code
   - Include rollback procedures for failed migrations

2. **Environment Configuration**:
   - Use Kubernetes Secrets or Docker secrets for sensitive data
   - Create environment-specific configuration files
   - Validate all configurations during startup

3. **Monitoring Setup**:
   - Deploy Prometheus for metrics collection
   - Set up Grafana dashboards for visualization
   - Configure alerting for critical thresholds

4. **Load Testing**:
   - Perform load testing before each major release
   - Establish baseline performance metrics
   - Document scaling requirements

5. **Backup Strategy**:
   - Schedule regular database backups
   - Test restoration procedures periodically
   - Implement point-in-time recovery capability
---


## 👥 Contributing

We welcome contributions to ObjectVision Backend! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Follow the coding standards and style guide
   - Add tests for new features
   - Update documentation as needed
4. **Run the tests**:
   ```bash
   npm test
   ```
5. **Submit a pull request**:
   - Provide a clear description of the changes
   - Reference any related issues
   - Include screenshots or GIFs for UI changes

---

## 🧯 Troubleshooting

Here are some common issues you might encounter while running the ObjectVision Backend and how to resolve them:

### 1. Docker Issues
- **Problem:** Containers won’t start or crash immediately
- **Solution:**
  - Run `docker-compose down -v` to remove volumes
  - Run `docker-compose up --build` again to rebuild images

### 2. Database Connection Errors
- **Problem:** Cannot connect to PostgreSQL
- **Solution:**
  - Ensure PostgreSQL container is running
  - Check `DATABASE_URL` in `.env` is correct
  - Try restarting the container using `docker-compose restart db`

### 3. Redis or Celery Errors
- **Problem:** Tasks not being picked up
- **Solution:**
  - Confirm Redis is running and accessible
  - Ensure Celery worker is started: `celery -A app.tasks.celery_app worker --loglevel=info`
  - Check logs for Celery startup errors

### 4. WebSocket Disconnects
- **Problem:** WebSocket closes unexpectedly
- **Solution:**
  - Check for errors in the browser console or backend logs
  - Ensure the WebSocket route is correctly implemented on the frontend

### 5. Environment Variable Issues
- **Problem:** App fails to start due to missing configurations
- **Solution:**
  - Ensure `.env.development` exists and is populated
  - Refer to `.env.example` for required keys

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Project Maintainer**: SK Imtiaj Uddin
- **Email**: imtiaj.kol@gmail.com
- **GitHub**: [@imtiaj-007](https://github.com/imtiaj-007)
- **LinkedIn**: [@sk-imtiaj-uddin](https://www.linkedin.com/in/sk-imtiaj-uddin-b26432254/)
- **Twitter**: [@imtiaj_007](https://x.com/imtiaj_007)

---

<p style="font-size:18px; text-align:center">Made with ❤️ by the ObjectVision Team</p>

