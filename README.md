# AI SkillGap & Job Recommendation System

A working SIH Level-3 prototype that extracts catalog skills from resumes, compares a profile with sample roles, ranks jobs using explainable content matching, and builds a learning plan from skill gaps.

## Problem and Solution

Students often have difficulty translating coursework and projects into job requirements. This prototype provides a guided workflow: add skills manually or upload a resume, choose a target role, inspect matched and missing requirements, compare recommended jobs, and follow official learning resources.

## Features

- PDF, DOCX, and TXT resume text extraction with normalized skill aliases.
- 30 seeded job listings and an expandable categorized skill catalog.
- Required-skill coverage and TF-IDF/cosine content similarity for job ranking.
- Optional profile context for education, experience, preferred role, and location.
- Skill-gap analysis, a missing-skill roadmap, and course links from official documentation and learning platforms.
- Optional student registration/login, bcrypt password hashes, signed JWTs, and editable MongoDB-backed profiles.
- Admin-protected job, skill, and course CRUD endpoints. Admin role assignment is controlled by `ADMIN_EMAILS`.
- MongoDB is optional for the public demo endpoints; persistence, accounts, and administration require MongoDB.

## Architecture

```text
React + Vite dashboard
  -> FastAPI REST API
      -> ML modules: extraction, skill gaps, TF-IDF recommendations, roadmap
      -> MongoDB collections and seeded catalogs (optional for demo mode)
```

The matching score is deterministic and explainable. Required-skill coverage is combined with TF-IDF cosine similarity:

`recommendation score = 0.75 × required-skill coverage + 0.25 × cosine similarity`

The skill-gap percentage is `matched required skills / total required skills × 100`. The recommender uses candidate skills and, when provided, education, experience, preferred role, and preferred location in its profile text. It is a lightweight content-based baseline, not a trained predictive model.

## Technology

- Frontend: React, JavaScript, Vite, Axios, Lucide icons, responsive CSS.
- Backend: Python, FastAPI, Pydantic, PyMongo.
- Matching: scikit-learn TF-IDF and cosine similarity; controlled skill dictionary for resume extraction.
- Resume readers: PyMuPDF and python-docx.
- Database: MongoDB.

## Project Structure

```text
backend/
  app/main.py             API routes and request schemas
  app/auth.py             password hashing and JWT authorization
  app/database.py         MongoDB connection
  app/seed.py             sample jobs, skills, and courses
  app/ml/                 skill extraction, gap analysis, recommendations
  tests/                  backend behavior tests
frontend/
  src/main.jsx            dashboard and API integration
  src/app.css             application styles
```

## Installation

Prerequisites: Python 3.10+, Node.js 20+, and MongoDB for persistent accounts/admin data.

### Backend (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and set `JWT_SECRET_KEY` to a long random value. Add the email address that should receive admin access to `ADMIN_EMAILS`; register that address through the app after MongoDB is running. Never use the example value for a deployed system.

Start the API:

```powershell
uvicorn app.main:app --reload
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### Frontend

Open another PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite. The default API origin is `http://127.0.0.1:8000`. Set `VITE_API_URL` in `frontend/.env` to use another backend origin.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `MONGO_URI` | MongoDB connection string; defaults to local MongoDB. |
| `DB_NAME` | Database name; defaults to `skillgap_db`. |
| `JWT_SECRET_KEY` | Required to issue/verify login tokens. |
| `ADMIN_EMAILS` | Comma-separated addresses granted admin role at registration. |
| `CORS_ORIGINS` | Comma-separated frontend origins allowed by the API. |
| `VITE_API_URL` | Optional frontend API origin. |

The public demo endpoints fall back to in-code catalogs when MongoDB is unavailable. Registration, login, profile persistence, and admin operations need a reachable MongoDB instance and a configured JWT secret.

## MongoDB Setup

Start a local MongoDB server or configure `MONGO_URI`. The API creates unique indexes for user email, job IDs, skill names, and course IDs, then seeds the sample job and skill catalogs. Course records are seeded the first time the course catalog is requested. Collections include `users`, `jobs`, `skills`, and `courses`; additional progress/recommendation persistence can be added as the prototype expands.

## Demo Workflow

The dashboard starts with Arun Kumar's sample skill set: Python, SQL, Git, HTML, and CSS. Upload a resume or adjust skills, select Machine Learning Engineer or another role, run the analysis, and inspect matched skills, missing skills, ranked roles, roadmap steps, and course links. Results are computed from the selected profile and seeded job records, not random values.

To use account persistence, start MongoDB, configure the backend environment, then register or sign in from the dashboard. Admin users are determined by the configured `ADMIN_EMAILS` allowlist.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/auth/register` | Create student account and return bearer token. |
| `POST` | `/api/auth/login` | Verify credentials and return bearer token. |
| `GET` / `PUT` | `/api/profile` | Read or update authenticated profile. |
| `GET` | `/api/jobs` | List seeded or stored jobs. |
| `GET` | `/api/jobs/{job_id}` | Retrieve one job by ID. |
| `GET` | `/api/skills` | List canonical skills. |
| `POST` | `/api/skills` | Admin-only skill creation. |
| `GET` | `/api/courses` | List learning resources. |
| `GET` | `/api/courses/recommended?skills=Python` | Recommend resources for skills not in the supplied profile. |
| `POST` | `/api/resume/upload` | Multipart field `file`; accepts PDF/DOCX/TXT up to 5 MB. |
| `POST` | `/api/analyze` | Compare submitted skills with a job ID. |
| `GET` | `/api/analysis/skill-gap/{job_id}?skills=Python` | Query-string form of skill-gap analysis. |
| `POST` | `/api/recommend` | Rank jobs from skills and optional profile fields. |
| `GET` | `/api/recommendations/jobs?skills=Python` | Query-string form of job recommendations. |
| `POST` | `/api/roadmap` | Generate steps from missing job skills. |
| `GET` | `/api/roadmap?job_id=JOB003&skills=Python` | Query-string form of roadmap generation. |
| `POST` | `/api/roadmap/generate` | Alias for roadmap generation. |
| `POST` / `PUT` / `DELETE` | `/api/admin/jobs...` | Admin-only job management. |
| `POST` / `PUT` / `DELETE` | `/api/admin/skills...` | Admin-only skill management. |
| `POST` / `PUT` / `DELETE` | `/api/admin/courses...` | Admin-only course management. |
| `GET` | `/api/admin/users`, `/api/admin/stats` | Admin-only user list and summary statistics. |

Protected endpoints accept `Authorization: Bearer <token>`. FastAPI also exposes the generated OpenAPI schema at `/openapi.json`.

## Tests

From `backend`:

```powershell
python -m unittest discover -s tests
```

The suite covers resume skill extraction, alias normalization, gap percentages, TF-IDF and profile-aware ranking, roadmap generation, upload handling, password hashing, JWT claims, and core route/data contracts.

## Screenshots

Add dashboard, resume analysis, and roadmap screenshots here when captured from a configured local run.

## Prototype Scope and Future Work

This repository currently provides a single responsive student dashboard and backend admin APIs. Separate landing/register/login pages, admin management screens, persistent resume storage, progress tracking, charts, and end-to-end browser tests remain future work. Additional ideas include LLM-based resume feedback, interview preparation, voice assistance, live job APIs, LinkedIn integration, semantic embeddings, salary prediction, and career trajectory prediction.#   S k i l l - G a p - A N D - J - R  
 