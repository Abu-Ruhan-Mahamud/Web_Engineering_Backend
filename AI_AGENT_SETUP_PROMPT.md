# AI Agent Setup Prompt

Copy and paste the following prompt into your VS Code AI agent (GitHub Copilot Chat, Cursor, etc.) after opening the project folder:

---

## The Prompt

```
I need you to set up this Curova Healthcare project on my Windows system. Follow these steps exactly:

### 1. Database Setup
- I need PostgreSQL running. Help me create a database called `curova_db` with user `curova_user`. Guide me through connecting to PostgreSQL via command line (psql -U postgres) and running these SQL commands:

CREATE DATABASE curova_db;
CREATE USER curova_user WITH PASSWORD 'curova_pass_2026';
GRANT ALL PRIVILEGES ON DATABASE curova_db TO curova_user;
ALTER DATABASE curova_db OWNER TO curova_user;

If psql is not in my PATH, help me find it (usually at C:\Program Files\PostgreSQL\16\bin\psql.exe).

### 2. Backend Setup
Run these commands in sequence (wait for each to finish):

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

### 3. Environment File
Create the file `backend/.env` with this content:

SECRET_KEY=django-insecure-curova-dev-key-change-in-production-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=curova_db
DB_USER=curova_user
DB_PASSWORD=curova_pass_2026
DB_HOST=127.0.0.1
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

### 4. Run Migrations & Seed Data
With the venv still activated:

python manage.py migrate
python manage.py seed_data

The seed_data command will create demo users. Note the credentials it prints.

### 5. Start Backend Server
python manage.py runserver

Keep this running.

### 6. Frontend Setup (in a new terminal)
cd frontend
npm install
npm run dev

### 7. Verify
Open http://localhost:5173 in the browser and confirm the login page loads.
Try logging in with patient@curova.com / Patient@123

Important notes:
- The backend MUST be running on port 8000 (default) for the frontend API calls to work.
- The frontend runs on port 5173 (Vite default).
- If PostgreSQL is not installed, I need to install it first from https://www.postgresql.org/download/windows/ — during install, remember the postgres superuser password.
- If Python is not installed, get it from https://www.python.org/downloads/ — check "Add to PATH" during install.
- If Node.js is not installed, get it from https://nodejs.org/ (LTS version).

Please execute each step, show me the output, and confirm success before moving to the next step. If any step fails, help me troubleshoot it.
```
Detailed setup guide can be found at WINDOWS_SETUP.md
---

## Notes for the human

- If your PostgreSQL port is different from 5432, update both the SQL connection and the `.env` file.
- The password `curova_pass_2026` in the prompt above is just a dev default — change it if you want.
- After setup, read `WINDOWS_SETUP.md` for the full project structure and troubleshooting tips.
