import os
import re
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError
from .auth import admin_user, create_access_token, current_user, hash_password, verify_password
from .database import get_db
from .ml import extract_skills, skill_gap, recommend_jobs
from .ml.skill_extractor import SKILLS, canonical_skill
from .ml.skill_gap import build_roadmap
from .seed import get_courses, seed_database, seed_skills

app = FastAPI(title="AI SkillGap & Job Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    try:
        db = get_db()
        db.users.create_index("email", unique=True)
        db.jobs.create_index("job_id", unique=True)
        db.skills.create_index("name", unique=True)
        db.courses.create_index("course_id", unique=True)
        seed_database()
        seed_skills()
    except Exception:
        pass

class AnalyzeRequest(BaseModel):
    skills: list[str]
    job_id: str

class RecommendRequest(BaseModel):
    skills: list[str]
    education: str = ""
    experience: str = ""
    preferred_job_role: str = ""
    preferred_location: str = ""

class RoadmapRequest(BaseModel):
    skills: list[str]
    job_id: str

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=72)

class LoginRequest(BaseModel):
    email: str
    password: str

class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    education: str | None = Field(default=None, max_length=160)
    degree: str | None = Field(default=None, max_length=120)
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)
    experience: str | None = Field(default=None, max_length=120)
    location: str | None = Field(default=None, max_length=120)
    preferred_job_role: str | None = Field(default=None, max_length=120)
    preferred_location: str | None = Field(default=None, max_length=120)
    skills: list[str] | None = None
    certifications: list[str] | None = None

class JobInput(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    company: str = Field(min_length=2, max_length=120)
    location: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10, max_length=5000)
    required_skills: list[str] = Field(min_length=1)
    preferred_skills: list[str] = Field(default_factory=list)
    education: str = ""
    experience: str = ""
    salary_range: str = "Not specified"
    employment_type: str = "Full-time"

class SkillInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    category: str = Field(min_length=1, max_length=80)

class CourseInput(BaseModel):
    course_name: str = Field(min_length=2, max_length=160)
    skill: str = Field(min_length=1, max_length=80)
    level: str = Field(min_length=1, max_length=40)
    duration: str = Field(min_length=1, max_length=80)
    platform: str = Field(min_length=1, max_length=80)
    url: str = Field(min_length=8, max_length=500)
    description: str = Field(min_length=10, max_length=1000)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AI SkillGap API"}

@app.post("/api/auth/register", status_code=201)
def register(req: RegisterRequest):
    email = req.email.strip().casefold()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise HTTPException(422, "Enter a valid email address")
    db = get_db()
    admin_emails = {value.strip().casefold() for value in os.getenv("ADMIN_EMAILS", "").split(",") if value.strip()}
    user = {
        "name": req.name.strip(),
        "email": email,
        "password_hash": hash_password(req.password),
        "role": "admin" if email in admin_emails else "student",
        "skills": [],
        "certifications": [],
    }
    access_token = create_access_token(email, user["role"])
    try:
        db.users.insert_one(user)
    except DuplicateKeyError as exc:
        raise HTTPException(409, "An account with this email already exists") from exc
    except Exception as exc:
        raise HTTPException(503, "User database is unavailable") from exc
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}

@app.post("/api/auth/login")
def login(req: LoginRequest):
    try:
        user = get_db().users.find_one({"email": req.email.strip().casefold()})
    except Exception as exc:
        raise HTTPException(503, "User database is unavailable") from exc
    if not user or not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": create_access_token(user["email"], user["role"]), "token_type": "bearer", "role": user["role"]}

@app.get("/api/profile")
def get_profile(user=Depends(current_user)):
    profile = get_db().users.find_one({"email": user["email"]}, {"_id": 0, "password_hash": 0})
    return {"profile": profile}

@app.put("/api/profile")
def update_profile(req: ProfileUpdate, user=Depends(current_user)):
    fields = req.model_dump(exclude_unset=True)
    if "skills" in fields and fields["skills"] is not None:
        fields["skills"] = list(dict.fromkeys(skill.strip() for skill in fields["skills"] if skill.strip()))
    if fields:
        get_db().users.update_one({"email": user["email"]}, {"$set": fields})
    return get_profile(user)

@app.get("/api/skills")
def get_skills():
    try:
        skills = list(get_db().skills.find({}, {"_id": 0}))
        if skills:
            return {"skills": [skill["name"] for skill in skills]}
    except Exception:
        pass
    return {"skills": SKILLS}

@app.post("/api/admin/jobs", status_code=201)
def create_job(req: JobInput, user=Depends(admin_user)):
    job = req.model_dump()
    job["job_id"] = f"JOB-{uuid.uuid4().hex[:10].upper()}"
    get_db().jobs.insert_one(job)
    return {"job": job}

@app.put("/api/admin/jobs/{job_id}")
def update_job(job_id: str, req: JobInput, user=Depends(admin_user)):
    job = req.model_dump()
    result = get_db().jobs.update_one({"job_id": job_id}, {"$set": job})
    if result.matched_count == 0:
        raise HTTPException(404, "Job not found")
    return {"job": {"job_id": job_id, **job}}

@app.delete("/api/admin/jobs/{job_id}", status_code=204)
def delete_job(job_id: str, user=Depends(admin_user)):
    if get_db().jobs.delete_one({"job_id": job_id}).deleted_count == 0:
        raise HTTPException(404, "Job not found")

@app.get("/api/admin/users")
def admin_users(user=Depends(admin_user)):
    users = list(get_db().users.find({}, {"_id": 0, "password_hash": 0}))
    return {"users": users, "total_users": len(users)}

@app.get("/api/admin/stats")
def admin_stats(user=Depends(admin_user)):
    db = get_db()
    jobs = get_jobs()["jobs"]
    demanded = {}
    for job in jobs:
        for skill in job.get("required_skills", []):
            demanded[skill] = demanded.get(skill, 0) + 1
    try:
        total_users = db.users.count_documents({})
        total_courses = db.courses.count_documents({}) or len(get_courses())
        total_skills = db.skills.count_documents({}) or len(SKILLS)
        total_recommendations = db.recommendations.count_documents({})
    except Exception as exc:
        raise HTTPException(503, "Admin statistics are unavailable") from exc
    return {
        "total_users": total_users,
        "total_jobs": len(jobs),
        "total_skills": total_skills,
        "total_courses": total_courses,
        "total_recommendations": total_recommendations,
        "most_demanded_skills": sorted(demanded.items(), key=lambda item: (-item[1], item[0]))[:10],
        "most_recommended_jobs": [],
    }

@app.post("/api/admin/skills", status_code=201)
@app.post("/api/skills", status_code=201)
def create_skill(req: SkillInput, user=Depends(admin_user)):
    skill = {"name": req.name.strip(), "category": req.category.strip()}
    try:
        get_db().skills.insert_one(skill)
    except DuplicateKeyError as exc:
        raise HTTPException(409, "Skill already exists") from exc
    return {"skill": skill}

@app.put("/api/admin/skills/{name}")
def update_skill(name: str, req: SkillInput, user=Depends(admin_user)):
    skill = {"name": req.name.strip(), "category": req.category.strip()}
    result = get_db().skills.update_one({"name": name}, {"$set": skill})
    if result.matched_count == 0:
        raise HTTPException(404, "Skill not found")
    return {"skill": skill}

@app.delete("/api/admin/skills/{name}", status_code=204)
def delete_skill(name: str, user=Depends(admin_user)):
    if get_db().skills.delete_one({"name": name}).deleted_count == 0:
        raise HTTPException(404, "Skill not found")

@app.post("/api/admin/courses", status_code=201)
def create_course(req: CourseInput, user=Depends(admin_user)):
    if not req.url.startswith(("https://", "http://")):
        raise HTTPException(422, "Course URL must use HTTP or HTTPS")
    course = req.model_dump()
    course["course_id"] = f"COURSE-{uuid.uuid4().hex[:10].upper()}"
    get_db().courses.insert_one(course)
    return {"course": course}

@app.put("/api/admin/courses/{course_id}")
def update_course(course_id: str, req: CourseInput, user=Depends(admin_user)):
    if not req.url.startswith(("https://", "http://")):
        raise HTTPException(422, "Course URL must use HTTP or HTTPS")
    course = req.model_dump()
    result = get_db().courses.update_one({"course_id": course_id}, {"$set": course})
    if result.matched_count == 0:
        raise HTTPException(404, "Course not found")
    return {"course": {"course_id": course_id, **course}}

@app.delete("/api/admin/courses/{course_id}", status_code=204)
def delete_course(course_id: str, user=Depends(admin_user)):
    if get_db().courses.delete_one({"course_id": course_id}).deleted_count == 0:
        raise HTTPException(404, "Course not found")

@app.get("/api/courses")
def courses():
    return {"courses": get_courses()}

@app.get("/api/courses/recommended")
def recommended_courses(skills: list[str] = Query(default=[])):
    known = {canonical_skill(skill).casefold() for skill in skills}
    gaps = [course for course in get_courses() if canonical_skill(course["skill"]).casefold() not in known]
    return {"courses": gaps}

@app.get("/api/jobs")
def get_jobs():
    try:
        jobs = list(get_db().jobs.find({}, {"_id": 0}))
        if jobs:
            return {"jobs": jobs}
    except Exception:
        pass
    return {"jobs": seed_database(return_jobs=True)}

@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = next((item for item in get_jobs()["jobs"] if item["job_id"] == job_id), None)
    if not job:
        raise HTTPException(404, "Job not found")
    return {"job": job}

@app.post("/api/analyze")
@app.post("/api/analysis/skills")
def analyze(req: AnalyzeRequest):
    jobs = get_jobs()["jobs"]
    job = next((j for j in jobs if j["job_id"] == req.job_id), None)
    if not job:
        raise HTTPException(404, "Job not found")
    return skill_gap(req.skills, job["required_skills"])

@app.get("/api/analysis/skill-gap/{job_id}")
def get_skill_gap(job_id: str, skills: list[str] = Query(default=[])):
    job = next((item for item in get_jobs()["jobs"] if item["job_id"] == job_id), None)
    if not job:
        raise HTTPException(404, "Job not found")
    return skill_gap(skills, job["required_skills"])

@app.post("/api/recommend")
def recommend(req: RecommendRequest):
    jobs = get_jobs()["jobs"]
    return {"recommendations": recommend_jobs(req.skills, jobs, req.model_dump(exclude={"skills"}))}

@app.get("/api/recommendations/jobs")
def get_recommendations(
    skills: list[str] = Query(default=[]),
    education: str = "",
    experience: str = "",
    preferred_job_role: str = "",
    preferred_location: str = "",
):
    jobs = get_jobs()["jobs"]
    profile = {
        "education": education,
        "experience": experience,
        "preferred_job_role": preferred_job_role,
        "preferred_location": preferred_location,
    }
    return {"recommendations": recommend_jobs(skills, jobs, profile)}

@app.post("/api/roadmap")
@app.post("/api/roadmap/generate")
def roadmap(req: RoadmapRequest):
    jobs = get_jobs()["jobs"]
    job = next((job for job in jobs if job["job_id"] == req.job_id), None)
    if not job:
        raise HTTPException(404, "Job not found")
    return build_roadmap(req.skills, job["required_skills"])

@app.get("/api/roadmap")
def get_roadmap(job_id: str, skills: list[str] = Query(default=[])):
    job = next((item for item in get_jobs()["jobs"] if item["job_id"] == job_id), None)
    if not job:
        raise HTTPException(404, "Job not found")
    return build_roadmap(skills, job["required_skills"])

@app.post("/api/resume/skills")
@app.post("/api/resume/upload")
async def resume_skills(file: UploadFile = File(...)):
    filename = file.filename or "resume.txt"
    if not filename.lower().endswith((".pdf", ".docx", ".txt")):
        raise HTTPException(400, "Upload a PDF, DOCX, or TXT resume")
    data = await file.read(5 * 1024 * 1024 + 1)
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(413, "Resume must be 5 MB or smaller")
    if not data:
        raise HTTPException(400, "Resume file is empty")
    try:
        skills = extract_skills(data, filename)
    except Exception as exc:
        raise HTTPException(400, "Could not read this resume file") from exc
    return {"filename": filename, "skills": skills}
