# ObjectVision Backend

Welcome to the **ObjectVision Backend** repository! This project powers the backend services for the ObjectVision application, designed for efficient and scalable object detection workflows.

## 🚀 Features
- FastAPI-powered RESTful APIs
- Asynchronous task management with Celery
- Redis for caching and task queuing
- Centralized dynamic email service with Brevo
- JWT Authentication with token blacklisting
- Containerized with Docker for easy deployment

---

## 📦 Project Structure
```
objectvision-backend/
├── app/
│   ├── configuration/      # App configuration files
│   ├── db/                 # Database models and migrations
│   ├── docs/               # API documentation
│   ├── handlers/           # Exception & Request handlers
│   ├── helpers/            # Helper functions
│   ├── middleware/         # Custom middleware
│   ├── performance/        # Performance optimizations
│   ├── repository/         # Database repository patterns
│   ├── routes/             # API route definitions
│   ├── schedulers/         # Scheduled background tasks
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic and integrations
│   ├── tasks/              # Celery tasks
│   ├── templates/          # Jinja email templates
│   ├── utils/              # Utility functions
│   └── main.py             # Application entry point
├── logs/                   # Log files
├── .env                    # Environment variables
├── .gitignore              # Git ignore rules
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## 🛠️ Prerequisites
- **Python 3.10+**
- **Docker & Docker Compose**
- **PostgreSQL**
- **Redis**

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/objectvision-backend.git
cd objectvision-backend
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
Create a `.env.development` file in the root directory:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/objectvision
SECRET_KEY=your_secret_key
REDIS_URL=redis://localhost:6379/0
BREVO_API_KEY=your_brevo_api_key
...
```
Look at `.env.example` file for detailed key information

### 5️⃣ Run Database Migrations
```bash
alembic upgrade head
```

### 6️⃣ Start the Application
```bash
uvicorn app.main:app --reload
```

The API will be available at: [http://localhost:8000](http://localhost:8000)

---

## 🐳 Run with Docker
```bash
docker-compose up --build
```

This will start:
- **FastAPI App** on `localhost:8000`
- **PostgreSQL** on `localhost:5432`
- **Redis** on `localhost:6379`
- **Celery Worker** for background tasks

---

## 🗃️ API Documentation
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🚀 Celery Task Management
Start the Celery worker:
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

To monitor tasks, run:
```bash
celery -A app.tasks.celery_app flower --port=5555
```
View dashboard at: [http://localhost:5555](http://localhost:5555)

---

## 🧪 Running Tests
```bash
pytest --cov=app tests/
```

---

## 🙌 Contributing
1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📜 License
This project is licensed under the **MIT License**.

---

## 📧 Contact
For any queries, reach out at **imtiaj.dev@gmail.com**

