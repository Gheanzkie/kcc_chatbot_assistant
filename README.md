# KCC Chatbot Assistant

An AI-powered knowledge companion chatbot built with Django and MySQL. Features a professional dark-themed UI, user management, and a welcome landing page.

## Developers

- **Ghean De La Cruz**
- **John Marie Alarcon**

## Admin Login

| Field    | Value            |
|----------|------------------|
| Email    | `admin@admin.com` |
| Username | `admin`           |
| Password | *(set during setup)* |

## Tech Stack

- **Framework:** Django 5.0.14
- **Database:** MySQL / MariaDB
- **UI:** Bootstrap 5 / Tabler CSS, Font Awesome 6
- **Python:** 3.13+

## Project Structure

```
kcc_chatbot_assistant/
├── apps/
│   ├── core/          # Welcome, login, logout, register, dashboard
│   └── users/         # User model, profile edit, user management CRUD
├── db/                # SQL database dump
│   └── kcc_chatbot.sql
├── mysite/            # Project settings, URLs, WSGI
├── static/            # CSS, JS, images (KCC logo)
├── templates/         # HTML templates (welcome, login, dashboard, sidebar)
└── requirements.txt
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/glenntheprogrammer/projectv3.git
cd projectv3
```

### 2. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install mysqlclient
```

### 4. Set up the database

```bash
# Create database in MySQL/MariaDB
mysql -u root -p -e "CREATE DATABASE kcc_chatbot CHARACTER SET utf8mb4;"

# Import the SQL dump
mysql -u root -p kcc_chatbot < db/kcc_chatbot.sql
```

### 5. Configure settings

Edit `mysite/settings.py` and update the `DATABASES` section:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'kcc_chatbot',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Also update `SECRET_KEY` and set `DEBUG = False` for production.

### 6. Run migrations (if not using the SQL dump)

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Run the server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the welcome page.

## Features

- **Welcome Page** — Professional dark-themed landing page with KCC branding
- **Authentication** — Email-based login, registration with validation
- **Dashboard** — Admin overview with user stats
- **User Management** — Superadmin can add, edit, and delete users via AJAX
- **Profile Editor** — Sidebar popup for editing profile and changing password
- **Responsive UI** — Mobile-friendly dark theme throughout

## Routes

| URL              | Description                  |
|------------------|------------------------------|
| `/`              | Welcome / landing page       |
| `/login/`        | Login page                   |
| `/register/`     | Registration page            |
| `/home/`         | Dashboard (requires login)   |
| `/users/`        | User management (superadmin) |
| `/users/profile/` | Profile / password edit     |
| `/admin/`        | Django admin panel           |

## Session Log

See [SESSION_LOG.md](SESSION_LOG.md) for the full development session log including security audit findings and bug fixes.
