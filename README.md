Match-Step is a lightweight, open-source web app that lets two people privately discover whether they’re on the same page about taking their relationship to the next level—without the fear of making the first move.
• FastAPI + SQLite, deploy-ready on Render/Railway
• Research-based survey (current-status & future-wishes) with double-consent matching
• Magic-link auth, personal history dashboard, and admin stats
• Tailwind UI with theme switcher (light | dark | pride)
Perfect for dorms, friend groups, or anyone who wants a risk-free “Are we both interested?” check.


# Me-Too 💬  
A private survey tool to help two people discover if they both want to take their relationship to the next level — without the fear of making the first move.

## ✨ Features

- 🧠 Research-based questions (current status & future wishes)
- 🔒 Magic-link authentication (no passwords)
- 🔁 Double-consent matching (only show mutual wishes)
- 📊 Personal response history & admin dashboard
- 🎨 Light, dark, and pride theme toggle
- 🪄 One-click deploy (FastAPI + SQLite)

## 🔧 Stack

- FastAPI + Jinja2
- Tailwind CSS
- SQLite (via SQLAlchemy)
- Itsdangerous (secure cookie & login token)
- No JS build step — works locally or on Render/Railway

---

## 🚀 Local Setup

1. Clone the repo  
   ```bash
   git clone https://github.com/yourname/me-too
   cd me-too
Create a virtualenv

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
Install requirements

bash
Copy
Edit
pip install -r requirements.txt
Run it

bash
Copy
Edit
export ADMIN_EMAIL=you@example.com
export SECRET_KEY=your-super-secret
uvicorn main:app --reload
Open in browser:

cpp
Copy
Edit
http://127.0.0.1:8000
Magic links will be printed in the terminal (for dev). You can later plug in SendGrid or Mailgun to send real emails.

📁 Project Structure
pgsql
Copy
Edit
me-too/
├── main.py                # All logic (survey, auth, dashboards)
├── questions.json         # Full survey schema (editable)
├── templates/             # Jinja2 HTML files
│   ├── base.html
│   ├── form.html
│   ├── result.html
│   ├── login.html
│   ├── history.html
│   └── admin.html
├── requirements.txt
└── responses.db           # SQLite database (auto-created)
🛠 Environment Variables
Variable	Description
SECRET_KEY	Your app’s signing key (for cookies & magic links)
ADMIN_EMAIL	Email address with access to /admin

📦 Deployment
Deploy to:

✅ Railway.app

✅ Render.com (use deploy command: uvicorn main:app --host 0.0.0.0 --port 10000)

✅ Fly.io or even Replit

SQLite is file-based — no extra DB needed to get started.
