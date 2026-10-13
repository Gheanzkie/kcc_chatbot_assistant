# KCC Chatbot Assistant — Session Log
**Date:** October 13, 2026
**Location:** C:\python\project\kcc_chatbot_assistant

---

## Session Summary

This session covered a full security scan, UI overhaul, app restructuring, and bug fixes for the KCC Chatbot Assistant Django project.

---

## 1. Security Scan (Static Analysis)

**Stack:** Django 5.0.14, MySQL/MariaDB, Bootstrap/Tabler UI

| # | Finding | Severity | Location |
|---|---------|----------|----------|
| F1 | Hardcoded SECRET_KEY committed to repo | HIGH | `mysite/settings.py:23` |
| F2 | DEBUG=True in shipped settings | HIGH | `mysite/settings.py:26` |
| F3 | MySQL root with empty password | HIGH | `mysite/settings.py:83-84` |
| F4 | No login rate limiting / lockout | MEDIUM | `apps/core/views.py:64-80` |
| F5 | User enumeration on register | MEDIUM | `apps/core/views.py:27,44` |
| F6 | CSRF logout via GET | LOW | `apps/core/views.py:83-85` |
| F7 | Dead/broken scoping helper | INFO | `apps/scoping.py` (deleted) |

**Clean:** stored XSS (uses `textContent`), CSRF on AJAX (sends X-CSRFToken), mass-assignment (superuser-gated).

---

## 2. App Restructuring

### Removed
- `apps/accounts/` — User model moved to users app
- `apps/chat/` — chat feature removed
- `apps/scoping.py` — dead code

### Moved
- **User model:** `apps/accounts/models.py` → `apps/users/models.py`
  - AbstractUser, email login (USERNAME_FIELD='email'), middle_name, birthday
  - `AUTH_USER_MODEL = 'users.User'`
  - `db_table = 'auth_user'`

### Added
- **Profile/password edit:** `apps/users/views.py: profile_edit` (AJAX JSON support)
- **Route:** `apps/users/urls.py: path('profile/', views.profile_edit, name='profile')`

### Current INSTALLED_APPS
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.core',
    'apps.users',
]
```

### Current URL Structure
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('users/', include('apps.users.urls')),
]
```

**Core URLs:**
- `/` → welcome page (anonymous) / redirect to dashboard (logged in)
- `/login/` → login
- `/logout/` → logout, redirect to welcome
- `/register/` → register
- `/home/` → dashboard

**Users URLs:**
- `/users/` → user list (superuser only)
- `/users/profile/` → profile/password edit (sidebar popup)
- `/users/ajax/list/`, `/users/ajax/get/`, `/users/ajax/save/`, `/users/ajax/delete/` → AJAX CRUD

---

## 3. UI Overhaul (Dark Theme)

### Color Scheme
- Background: `#0f172a → #1e293b → #0f172a` gradient
- Primary: `#0b6e4f` (dark emerald)
- Accent: `#10b981` (emerald)
- Text: `#e2e8f0` / `#94a3b8` / `#f8fafc`

### Templates Created/Rewritten

**`templates/welcome.html`** — Landing page
- Fixed glassmorphism navbar with KCC logo
- Hero section with floating logo animation
- "Get Started" → login, "Create Account" → register
- 6 feature cards (Smart Responses, 24/7, Knowledge Base, Secure, Instant, Built for Learning)
- Standalone (no base.html, no tabler.css)

**`templates/auth/login.html`** — Login page (rewritten)
- KCC logo + "KCC Assistant" branding
- Dark glassmorphism card
- Styled inputs with emerald focus ring
- Error alerts styled with red glass
- "Create one" link to register
- "Back to home" link to welcome
- Removed: tabler.css, Azuelo branding, dead lockout JS, missing demo.js

**`templates/theme/base.html`** — Base layout (rewritten)
- `data-bs-theme="dark"` on `<html>`
- KCC dark gradient background on body/page
- CSS overrides: sidebar, cards, tables, forms, buttons, footer, modals, alerts, pagination, badges
- Removed: 1300+ lines dead ApexCharts code, settings.html include, missing scripts

**`templates/theme/sidebar.html`** — Sidebar (rewritten)
- KCC logo in brand section
- Dashboard + Users (superuser only) nav links
- Mobile logout link
- **User card (lower-left):** avatar + username + role → opens edit popup
- **Edit Profile Modal** (popup):
  - Tabs: Profile (username/email/names/birthday) + Password (current/new/confirm)
  - AJAX submit with CSRF + X-Requested-With
  - Live sidebar name/avatar update on success
  - Success toast, modal auto-close with backdrop cleanup
  - Points to `users:profile`

**`templates/theme/footer.html`** — Dark themed footer

**`templates/home.html`** — Dashboard (rewritten)
- Stats cards: Total Users, Conversations (—), Messages (—), Active Today
- Welcome card with logo + "Manage Users" button
- Context from `home()` view: `total_users`, `active_today`

**`static/img/kcc_logo.png`** — Copied from `D:\GHEAN ALL PHOTOS\KCC_NEW_LOGO.png`

---

## 4. Bugs Fixed

### Migration Issues
1. **`apps/accounts/migrations/0001_initial.py` missing** — IndexError on runserver
   - Fixed: `makemigrations accounts` + `migrate --fake accounts`

2. **`apps.chat` name mismatch** — `ModuleNotFoundError: No module named 'chat'`
   - Fixed: `name = 'apps.chat'` in apps.py (app since deleted)

3. **`InconsistentMigrationHistory`** — admin.0001 before users.0001
   - Fixed: cleared all django_migrations records, `migrate --fake` all

4. **Stale migration records** — info, chat, accounts in DB after app removal
   - Fixed: `DELETE FROM django_migrations WHERE app IN ('accounts','info','chat')`

### Template Issues
5. **Welcome page fully white** — CSS values were stripped/empty
   - Fixed: rewrote all color values (hex codes were missing)

6. **`tabler.css` overriding dark theme** — body bg white
   - Fixed: removed tabler.css from welcome.html and login.html

7. **`home.html` missing `{% load static %}`** — TemplateSyntaxError
   - Fixed: added `{% load static %}` after `{% extends %}`

8. **`users/profile.html` TemplateDoesNotExist** — GET on /users/profile/
   - Fixed: GET redirects to dashboard (popup is the UI)

### View Issues
9. **`welcome_view` indented inside `register_view`** — AttributeError
   - Fixed: moved to module level

10. **`path('/', ...)` instead of `path('', ...)`** — 404 on root
    - Fixed: empty string for root URL

11. **`birthday` AttributeError** — `.strftime()` on string
    - Fixed: `user.refresh_from_db()` after save

12. **Modal backdrop not removed after update** — page unclickable
    - Fixed: `closeModal()` now force-removes `.modal-backdrop`, `modal-open`, inline overflow styles

### Import Issues (post-restructure)
13. **All `from apps.accounts.models import User`** → `from apps.users.models import User`
    - Fixed in: users/views.py, users/forms.py, core/views.py

---

## 5. Current Account
- **Email:** admin@admin.com
- **Username:** admin
- **Superuser:** True

---

## 6. Key File Map

```
kcc_chatbot_assistant/
├── manage.py
├── mysite/
│   ├── settings.py          # AUTH_USER_MODEL='users.User', INSTALLED_APPS
│   ├── urls.py              # admin + core + users
│   └── wsgi.py
├── apps/
│   ├── core/
│   │   ├── views.py         # welcome, login, logout, register, home(dashboard)
│   │   └── urls.py          # '', login/, home/, logout/, register/
│   ├── users/
│   │   ├── models.py        # User (AbstractUser, email login)
│   │   ├── views.py         # profile_edit, user_list_page, AJAX CRUD
│   │   ├── urls.py          # profile/, '', ajax/*
│   │   ├── forms.py         # UserForm
│   │   └── migrations/
│   │       └── 0001_initial.py
│   └── __init__.py
├── templates/
│   ├── welcome.html         # Landing page (dark, standalone)
│   ├── home.html            # Dashboard (stats + welcome card)
│   ├── auth/
│   │   ├── login.html       # Login (dark theme)
│   │   └── register.html    # Register
│   ├── users/
│   │   └── list.html        # User management (AJAX CRUD)
│   └── theme/
│       ├── base.html        # Base layout (dark overrides)
│       ├── sidebar.html     # Sidebar + edit profile modal
│       ├── footer.html      # Dark footer
│       └── settings.html    # Tabler theme settings (unused)
├── static/
│   ├── css/                 # tabler.css, app-theme.css, etc.
│   ├── js/                  # tabler.js, tabler-theme.js
│   ├── img/
│   │   └── kcc_logo.png     # KCC logo
│   └── libs/                # apexcharts, jsvectormap, list.js
└── requirements.txt         # Django==5.0.14
```

---

## 7. How to Run

```bash
cd C:\python\project\kcc_chatbot_assistant
.venv\Scripts\python manage.py runserver
```

- `/` → Welcome page (dark theme, KCC logo)
- Login as admin@admin.com → Dashboard
- Click lower-left user card → Edit Profile popup (Profile + Password tabs)
- `/users/` → User management (add/edit/delete users)
