[🇯🇵 日本語](README.md) | 🇺🇸 English

# StudyLog

StudyLog is a web app for systematically recording and organizing anything you want to track over time — study logs, journals, workout records, reading logs, and more.

Just like a folder structure on your PC, you can build hierarchical categories and accumulate records as time goes on.

🔗 **Live URL:** https://studylog-03pu.onrender.com

Sign in with your Google account to use the app. Your data is isolated per user and can never be viewed or edited by anyone else. Each log can be toggled public or private individually, and public logs can be viewed without logging in. From the login screen, "View public logs as guest" takes you straight to the public log list without signing in.

---

## 📌 Concept

"Anything with a meaningful change over time benefits from a systematic hierarchical structure."

Beyond study logs, StudyLog works for anything you want to keep recording continuously — journals, a child's growth records, reading logs, and more.

---

## 🖥️ Screens

```
Login screen
  └── Category selection (Screen 1)
        └── Subcategories + log list (Screen 2)
              └── Log detail (Screen 3)

Public log list (no login required)
  └── Public log detail (no login required)
```

**Screen 1 - Category Selection**
The landing page after login. Manage top-level categories in the sidebar.

**Screen 2 - Subcategories + Log List**
Shows subcategories under a category, and a list of logs with date and title.

**Screen 3 - Log Detail**
Shows a log's details (title, memo, open questions). Memo and open questions can be edited and saved in place. You can also toggle public/private from this screen.

**Public Log List / Detail**
Logs set to public can be viewed by anyone without logging in.

The layout is fully responsive for both PC and mobile. On mobile, you navigate through category → subcategory → log by tapping through each level.

---

## ⚙️ Tech Stack

| Category | Technology |
|---|---|
| Frontend | HTML / CSS / JavaScript |
| Backend | FastAPI |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Auth | Google OAuth (Google Identity Services) + JWT |
| Hosting | Render |

---

## 🚀 Key Features

- Google OAuth login with per-user data isolation
- Three-tier hierarchy: category / subcategory / detailed log
- Create, edit, and delete at every level (via the `···` dropdown menu)
- Cascading delete for categories/subcategories (deletes all child data, with a warning before deletion)
- Memo and open-questions fields on each log (supports line breaks)
- Per-log public/private toggle; public logs and their list are viewable without login
- Guest-mode entry point on the login screen (view the public log list without signing in)
- Slide-out sidebar for the category list
- Responsive design for both PC and mobile

---

## 🗂️ Directory Structure

```
StudyLog/
├── frontend/
│   ├── login.html       # Login screen
│   ├── index.html       # Category selection screen
│   ├── category.html    # Subcategory + log list screen
│   ├── log.html         # Log detail screen
│   ├── public.html      # Public log list screen (no login required)
│   ├── public-log.html  # Public log detail screen (no login required)
│   └── auth.js          # Shared auth logic (token management, fetch wrapper)
├── backend/
│   ├── main.py          # API endpoint definitions
│   ├── database.py      # DB connection setup
│   ├── models.py        # Table definitions
│   ├── auth.py          # Google auth / JWT issuing & verification
│   └── requirements.txt # Dependencies
└── .gitignore
```

---

## 🔧 Running Locally

### Prerequisites
- Python 3.11+
- PostgreSQL (or a hosted DB such as Supabase)
- A Google Cloud Console OAuth client ID

### Setup

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
# Create backend/.env with the following:
DATABASE_URL=postgresql://localhost/studylog
GOOGLE_CLIENT_ID=(your Google Cloud OAuth client ID)
JWT_SECRET_KEY=(a random string)

# Start the server
cd backend
uvicorn main:app --reload
```

Open `frontend/login.html` via a local server, not by double-clicking the file directly — Google Sign-In does not work over a `file://` URL.

---

## 📋 API Reference

| Resource | Method | Endpoint | Auth |
|---|---|---|---|
| Auth | POST | /auth/google (exchange a Google token for a JWT) | No |
| Auth | GET | /auth/me (get current user info) | Yes |
| Category | GET | /categories | Yes |
| Category | POST | /categories | Yes |
| Category | PUT | /categories/{id} | Yes |
| Category | DELETE | /categories/{id} (cascading delete) | Yes |
| Subcategory | GET | /subcategories/{category_id} | Yes |
| Subcategory | POST | /subcategories | Yes |
| Subcategory | PUT | /subcategories/{id} | Yes |
| Subcategory | DELETE | /subcategories/{id} (cascading delete) | Yes |
| Log | GET | /logs/{subcategory_id} | Yes |
| Log | GET | /logs/detail/{id} | Yes |
| Log | POST | /logs | Yes |
| Log | PUT | /logs/{id} | Yes |
| Log | DELETE | /logs/{id} | Yes |
| Public Log | GET | /public/logs (public log list) | No |
| Public Log | GET | /public/logs/{id} (public log detail) | No |

All endpoints marked "Yes" require an `Authorization: Bearer <JWT>` header.

---

## 🔒 Security

- IDOR protection: every CRUD endpoint only operates on the requesting user's own data
- CORS restricted to the production URL and local development environments only
- Data minimization: the user's Google email is never stored — only the immutable `google_id` is used for authentication
- User input (category names, log titles, etc.) is rendered safely as text to prevent HTML injection
- Duplicate-submission guard on save buttons to prevent accidental duplicate creation

---

## 📜 Version History

| Version | Notes |
|---|---|
| Ver1.0 | Initial release. 3 frontend screens, FastAPI + PostgreSQL backend, frontend/backend integration |
| Ver1.1 | Full CRUD from the UI. Cascading delete with warnings. Published on GitHub, deployed on Render |
| Ver1.2 | UX improvements (separated log creation from memo editing, added `···` dropdown menus). Visual redesign. Responsive layout for PC/mobile. Migrated database to Supabase |
| Ver2.0 | Added Google OAuth authentication with per-user data isolation. Added public/private toggle for logs. Strengthened security: CORS restriction, data minimization, HTML injection prevention |
| Ver2.1 | Added a "View public logs as guest" entry point on the login screen, allowing direct access to the public log list without signing in |

---

## 🔮 Roadmap

- Per-user timezone support
- Variable-depth hierarchy (users can decide how deep to go)
- Image attachments in memos
- AI comprehension quiz feature (auto-generate questions from what the user has entered)
- Redesign to merge the memo and open-questions fields into one
