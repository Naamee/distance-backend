# Distance Backend

A Flask-based backend for the Distance application.

---

## Installation

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd distance-backend
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

---

## Configuration

1. Set the Flask application environment variable:

```bash
export FLASK_APP=distance_app/__init__.py  # Linux / macOS
set FLASK_APP=distance_app/__init__.py     # Windows
```

2. Configure any environment variables (database URI, secret keys, etc.) in `.env` or directly in your environment.

---

## Running the Server

Start the Flask development server:

```bash
flask --app distance_app run
```

The server will run by default on `http://127.0.0.1:5000/`.

---

## Database Migrations

This project uses **Flask-Migrate** for database migrations.

- **Create a new migration:**

```bash
flask db migrate -m "<migration_file_name>"
```

- **Apply migrations:**

```bash
flask db upgrade
```

- **Rollback last migration:**

```bash
flask db downgrade
```

---
