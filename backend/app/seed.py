from .database import get_db
from .ml.skill_extractor import SKILLS

SKILL_CATEGORIES = {
    **{name: "Programming" for name in ("Python", "Java", "C", "C++", "JavaScript", "TypeScript")},
    **{name: "Web" for name in ("HTML", "CSS", "React", "Node.js", "Django", "Flask", "FastAPI")},
    **{name: "Database" for name in ("MySQL", "PostgreSQL", "MongoDB", "SQL", "Redis")},
    **{name: "Data & AI" for name in ("Pandas", "NumPy", "Matplotlib", "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Scikit-learn", "TensorFlow", "PyTorch", "Statistics")},
    **{name: "Cloud & DevOps" for name in ("AWS", "Azure", "Docker", "Kubernetes", "Git", "GitHub", "Linux")},
    **{name: "Other" for name in ("Excel", "Networking", "Cybersecurity")},
}

def _job(job_id, title, company, location, description, required, preferred, education, experience, salary, employment):
    return {
        "job_id": job_id,
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "required_skills": required,
        "preferred_skills": preferred,
        "education": education,
        "experience": experience,
        "salary_range": salary,
        "employment_type": employment,
    }


JOBS = [
    _job("JOB001", "Python Developer", "DemoTech", "Bengaluru", "Build Python backend services and REST APIs for a financial platform.", ["Python", "FastAPI", "SQL", "Git"], ["Docker", "AWS"], "B.Tech or equivalent", "0-2 years", "INR 5-9 LPA", "Full-time"),
    _job("JOB002", "Data Analyst", "DataWorks", "Chennai", "Analyze business datasets, build dashboards, and communicate measurable findings.", ["Python", "SQL", "Pandas", "NumPy", "Matplotlib"], ["Statistics", "Excel"], "Bachelor's in CS, Statistics, or related field", "0-2 years", "INR 4-8 LPA", "Full-time"),
    _job("JOB003", "Machine Learning Engineer", "AI Labs", "Hyderabad", "Develop, evaluate, and deploy supervised machine learning models.", ["Python", "Pandas", "NumPy", "Machine Learning", "Scikit-learn", "Git"], ["Docker", "AWS"], "B.Tech or M.Tech in CS or related field", "1-3 years", "INR 8-16 LPA", "Full-time"),
    _job("JOB004", "Full Stack Developer", "WebNova", "Pune", "Deliver responsive web products across React interfaces and Node.js services.", ["HTML", "CSS", "JavaScript", "React", "Node.js", "MongoDB", "Git"], ["TypeScript", "Docker"], "B.Tech or equivalent", "0-3 years", "INR 6-12 LPA", "Full-time"),
    _job("JOB005", "Backend Developer", "CloudApps", "Coimbatore", "Create scalable APIs, background services, and database integrations.", ["Python", "FastAPI", "MongoDB", "SQL", "Git"], ["Redis", "Docker"], "Bachelor's in CS or equivalent experience", "1-3 years", "INR 6-11 LPA", "Full-time"),
    _job("JOB006", "AI Engineer", "VisionAI", "Chennai", "Build practical AI and NLP prototypes and evaluate model quality.", ["Python", "Machine Learning", "NLP", "Pandas", "Scikit-learn"], ["PyTorch", "FastAPI"], "B.Tech or M.Tech in CS, AI, or related field", "0-3 years", "INR 7-14 LPA", "Full-time"),
    _job("JOB007", "Cloud Engineer", "CloudWorks", "Bengaluru", "Operate secure cloud environments and automate application deployments.", ["AWS", "Docker", "Linux", "Git", "Python"], ["Kubernetes", "Azure"], "Bachelor's in CS, IT, or related field", "1-3 years", "INR 7-14 LPA", "Full-time"),
    _job("JOB008", "Frontend Developer", "UI Labs", "Chennai", "Build accessible, responsive interfaces for analytics products.", ["HTML", "CSS", "JavaScript", "React", "Git"], ["TypeScript", "Node.js"], "B.Tech or equivalent", "0-2 years", "INR 5-10 LPA", "Full-time"),
    _job("JOB009", "Java Developer", "NexGen Systems", "Hyderabad", "Develop maintainable Java services for enterprise operations.", ["Java", "SQL", "Git", "Linux"], ["Docker", "AWS"], "B.Tech in CS or related field", "0-2 years", "INR 5-10 LPA", "Full-time"),
    _job("JOB010", "Java Developer", "FinEdge", "Mumbai", "Implement reliable Java applications and relational data workflows.", ["Java", "MySQL", "SQL", "Git"], ["Docker", "AWS"], "Bachelor's in CS or equivalent", "2-4 years", "INR 9-16 LPA", "Full-time"),
    _job("JOB011", "Data Scientist", "InsightSpring", "Bengaluru", "Build statistical models and communicate evidence-based product insights.", ["Python", "Pandas", "NumPy", "Statistics", "Machine Learning"], ["Scikit-learn", "SQL"], "M.Sc. or B.Tech in a quantitative field", "1-3 years", "INR 8-16 LPA", "Full-time"),
    _job("JOB012", "Data Scientist", "QuantLeaf", "Pune", "Explore large datasets and prototype predictive analytics solutions.", ["Python", "SQL", "Pandas", "Statistics", "Scikit-learn"], ["Matplotlib", "NumPy"], "Bachelor's or Master's in CS, Math, or Statistics", "0-2 years", "INR 7-13 LPA", "Full-time"),
    _job("JOB013", "Machine Learning Engineer", "ModelForge", "Remote", "Train and productionize recommendation and classification models.", ["Python", "NumPy", "Pandas", "Machine Learning", "Scikit-learn"], ["Docker", "Kubernetes"], "B.Tech or M.Tech in CS or related field", "2-4 years", "INR 12-22 LPA", "Full-time"),
    _job("JOB014", "AI Engineer", "CogniWorks", "Noida", "Prototype language and vision features and integrate them into product APIs.", ["Python", "NLP", "Machine Learning", "FastAPI"], ["PyTorch", "Docker"], "Bachelor's in CS, AI, or related field", "1-3 years", "INR 8-15 LPA", "Full-time"),
    _job("JOB015", "Backend Developer", "API Harbor", "Remote", "Design service APIs and data access layers for a SaaS platform.", ["JavaScript", "Node.js", "MongoDB", "SQL", "Git"], ["Docker", "AWS"], "B.Tech or equivalent experience", "1-3 years", "INR 7-13 LPA", "Full-time"),
    _job("JOB016", "Frontend Developer", "PixelNorth", "Mumbai", "Ship polished, accessible React experiences with reusable components.", ["JavaScript", "TypeScript", "React", "HTML", "CSS"], ["Node.js", "Git"], "Bachelor's in CS, design, or equivalent experience", "1-3 years", "INR 7-14 LPA", "Full-time"),
    _job("JOB017", "DevOps Engineer", "ReleaseGrid", "Bengaluru", "Automate CI/CD pipelines and improve the reliability of cloud services.", ["Linux", "Docker", "Kubernetes", "Git", "AWS"], ["Python", "Azure"], "Bachelor's in CS or IT", "1-3 years", "INR 8-16 LPA", "Full-time"),
    _job("JOB018", "Cybersecurity Analyst", "SentinelPoint", "Delhi", "Monitor security events, investigate incidents, and recommend mitigations.", ["Linux", "Python", "Networking", "Cybersecurity"], ["AWS", "SQL"], "Bachelor's in Cybersecurity, CS, or IT", "0-2 years", "INR 5-10 LPA", "Full-time"),
    _job("JOB019", "Python Developer", "BrightPath Tech", "Kochi", "Maintain data-heavy Python applications and write automated tests.", ["Python", "Django", "PostgreSQL", "Git"], ["Docker", "AWS"], "B.Tech or equivalent", "0-2 years", "INR 4-8 LPA", "Full-time"),
    _job("JOB020", "Data Analyst", "CivicMetrics", "Jaipur", "Turn operational data into clear reports and decision-support dashboards.", ["SQL", "Python", "Pandas", "Statistics"], ["Matplotlib", "Excel"], "Bachelor's in Statistics, Economics, or CS", "0-2 years", "INR 4-7 LPA", "Full-time"),
    _job("JOB021", "Cloud Engineer", "Skyward Digital", "Hyderabad", "Provision and support secure Azure infrastructure for application teams.", ["Azure", "Linux", "Docker", "Git"], ["Kubernetes", "Python"], "Bachelor's in CS or IT", "1-3 years", "INR 7-14 LPA", "Full-time"),
    _job("JOB022", "DevOps Engineer", "BuildStream", "Pune", "Maintain container platforms, release automation, and production observability.", ["Docker", "Kubernetes", "Linux", "Python", "Git"], ["AWS", "Azure"], "B.Tech or equivalent", "2-4 years", "INR 10-18 LPA", "Full-time"),
    _job("JOB023", "Cybersecurity Analyst", "ShieldLine", "Chennai", "Assess vulnerabilities and support incident response across cloud workloads.", ["Cybersecurity", "Linux", "AWS", "Python"], ["Azure", "Networking"], "Bachelor's in Cybersecurity or CS", "1-3 years", "INR 7-13 LPA", "Full-time"),
    _job("JOB024", "Full Stack Developer", "OrbitDesk", "Remote", "Build customer-facing workflows with React, TypeScript, and API services.", ["React", "TypeScript", "Node.js", "PostgreSQL", "Git"], ["Docker", "AWS"], "Bachelor's in CS or equivalent", "2-4 years", "INR 10-18 LPA", "Full-time"),
    _job("JOB025", "Machine Learning Engineer", "ForecastFoundry", "Mumbai", "Evaluate forecasting models and deploy reproducible ML pipelines.", ["Python", "Pandas", "Statistics", "Machine Learning", "Scikit-learn"], ["NumPy", "Docker"], "M.Tech or Master's in a quantitative field", "2-4 years", "INR 12-20 LPA", "Full-time"),
    _job("JOB026", "Data Analyst", "Northstar Retail", "Lucknow", "Analyze retail performance and build concise stakeholder reporting.", ["SQL", "Excel", "Statistics", "Python"], ["Pandas", "Matplotlib"], "Bachelor's in Business, Math, or CS", "0-2 years", "INR 3.5-7 LPA", "Full-time"),
    _job("JOB027", "Java Developer", "CoreLedger", "Remote", "Develop transaction processing services with attention to correctness and scale.", ["Java", "PostgreSQL", "Docker", "Git"], ["AWS", "Linux"], "B.Tech in CS or equivalent", "1-3 years", "INR 8-15 LPA", "Full-time"),
    _job("JOB028", "Python Developer", "GreenRoute", "Ahmedabad", "Create data ingestion and automation tools for logistics operations.", ["Python", "SQL", "Pandas", "Git"], ["FastAPI", "Docker"], "Bachelor's in CS, IT, or related field", "0-2 years", "INR 4-8 LPA", "Full-time"),
    _job("JOB029", "Backend Developer", "CareStack", "Kolkata", "Build secure backend services and integrations for digital health products.", ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"], ["AWS", "Redis"], "B.Tech or equivalent experience", "2-4 years", "INR 9-16 LPA", "Full-time"),
    _job("JOB030", "Cloud Engineer", "Monsoon Cloud", "Remote", "Support multi-environment cloud deployments and automate infrastructure tasks.", ["AWS", "Azure", "Linux", "Python", "Docker"], ["Kubernetes", "Git"], "Bachelor's in CS, IT, or engineering", "2-4 years", "INR 10-18 LPA", "Full-time"),
]

COURSES = [
    {"course_id": "COURSE001", "course_name": "Python Tutorial", "skill": "Python", "level": "Beginner", "duration": "Self-paced", "platform": "Python.org", "url": "https://docs.python.org/3/tutorial/", "description": "Official introduction to Python syntax and core concepts."},
    {"course_id": "COURSE002", "course_name": "NumPy Quickstart", "skill": "NumPy", "level": "Beginner", "duration": "2 hours", "platform": "NumPy", "url": "https://numpy.org/doc/stable/user/quickstart.html", "description": "Learn array operations and numerical computing fundamentals."},
    {"course_id": "COURSE003", "course_name": "Pandas Getting Started", "skill": "Pandas", "level": "Beginner", "duration": "3 hours", "platform": "Pandas", "url": "https://pandas.pydata.org/docs/getting_started/intro_tutorials/", "description": "Work through practical data loading, cleaning, and analysis tutorials."},
    {"course_id": "COURSE004", "course_name": "Statistics", "skill": "Statistics", "level": "Beginner", "duration": "Self-paced", "platform": "Khan Academy", "url": "https://www.khanacademy.org/math/statistics-probability", "description": "Build a foundation in probability, distributions, and statistical inference."},
    {"course_id": "COURSE005", "course_name": "Machine Learning with scikit-learn", "skill": "Machine Learning", "level": "Intermediate", "duration": "Self-paced", "platform": "scikit-learn", "url": "https://scikit-learn.org/stable/tutorial/index.html", "description": "Explore supervised learning workflows and model evaluation."},
    {"course_id": "COURSE006", "course_name": "Scikit-learn User Guide", "skill": "Scikit-learn", "level": "Intermediate", "duration": "Self-paced", "platform": "scikit-learn", "url": "https://scikit-learn.org/stable/user_guide.html", "description": "Learn estimators, preprocessing, model selection, and pipelines."},
    {"course_id": "COURSE007", "course_name": "SQL Tutorial", "skill": "SQL", "level": "Beginner", "duration": "Self-paced", "platform": "PostgreSQL", "url": "https://www.postgresql.org/docs/current/tutorial.html", "description": "Practice relational queries and database fundamentals."},
    {"course_id": "COURSE008", "course_name": "Git Book", "skill": "Git", "level": "Beginner", "duration": "Self-paced", "platform": "Git SCM", "url": "https://git-scm.com/book/en/v2", "description": "Learn version control workflows from basics through branching."},
    {"course_id": "COURSE009", "course_name": "React Learn", "skill": "React", "level": "Beginner", "duration": "Self-paced", "platform": "React", "url": "https://react.dev/learn", "description": "Build interfaces with components, state, and events."},
    {"course_id": "COURSE010", "course_name": "FastAPI Tutorial", "skill": "FastAPI", "level": "Intermediate", "duration": "Self-paced", "platform": "FastAPI", "url": "https://fastapi.tiangolo.com/tutorial/", "description": "Create validated Python APIs with dependency injection and OpenAPI."},
    {"course_id": "COURSE011", "course_name": "Docker Get Started", "skill": "Docker", "level": "Beginner", "duration": "2 hours", "platform": "Docker", "url": "https://docs.docker.com/get-started/", "description": "Containerize an application and learn the image build workflow."},
    {"course_id": "COURSE012", "course_name": "AWS Skill Builder", "skill": "AWS", "level": "Beginner", "duration": "Self-paced", "platform": "AWS", "url": "https://skillbuilder.aws/", "description": "Explore official cloud fundamentals and hands-on learning plans."},
    {"course_id": "COURSE013", "course_name": "Azure Fundamentals", "skill": "Azure", "level": "Beginner", "duration": "Self-paced", "platform": "Microsoft Learn", "url": "https://learn.microsoft.com/training/paths/azure-fundamentals-describe-cloud-concepts/", "description": "Study cloud concepts and the foundations of Microsoft Azure."},
    {"course_id": "COURSE014", "course_name": "Kubernetes Basics", "skill": "Kubernetes", "level": "Intermediate", "duration": "3 hours", "platform": "Kubernetes", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "description": "Deploy and scale a containerized application."},
    {"course_id": "COURSE015", "course_name": "JavaScript Guide", "skill": "JavaScript", "level": "Beginner", "duration": "Self-paced", "platform": "MDN", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "description": "Learn JavaScript language fundamentals and browser APIs."},
    {"course_id": "COURSE016", "course_name": "NLP Course", "skill": "NLP", "level": "Intermediate", "duration": "Self-paced", "platform": "spaCy", "url": "https://course.spacy.io/en/", "description": "Build practical natural language processing pipelines."},
    {"course_id": "COURSE017", "course_name": "PyTorch Tutorials", "skill": "PyTorch", "level": "Intermediate", "duration": "Self-paced", "platform": "PyTorch", "url": "https://pytorch.org/tutorials/", "description": "Learn tensor workflows and train neural networks."},
    {"course_id": "COURSE018", "course_name": "TensorFlow Tutorials", "skill": "TensorFlow", "level": "Intermediate", "duration": "Self-paced", "platform": "TensorFlow", "url": "https://www.tensorflow.org/tutorials", "description": "Build and train models with hands-on tutorials."},
    {"course_id": "COURSE019", "course_name": "Java Tutorials", "skill": "Java", "level": "Beginner", "duration": "Self-paced", "platform": "dev.java", "url": "https://dev.java/learn/", "description": "Learn Java language fundamentals and application development."},
    {"course_id": "COURSE020", "course_name": "TypeScript Handbook", "skill": "TypeScript", "level": "Intermediate", "duration": "Self-paced", "platform": "TypeScript", "url": "https://www.typescriptlang.org/docs/handbook/intro.html", "description": "Understand static typing and TypeScript's JavaScript integration."},
]

def seed_database(return_jobs=False):
    try:
        db = get_db()
        if return_jobs:
            jobs = list(db.jobs.find({}, {"_id": 0}))
            return jobs or JOBS
        for job in JOBS:
            current = db.jobs.find_one({"job_id": job["job_id"]})
            if not current or any(field not in current for field in job):
                db.jobs.update_one({"job_id": job["job_id"]}, {"$set": job}, upsert=True)
        return list(db.jobs.find({}, {"_id":0}))
    except Exception:
        return JOBS


def get_courses():
    try:
        db = get_db()
        if db.courses.count_documents({}) == 0:
            db.courses.insert_many(COURSES)
        return list(db.courses.find({}, {"_id": 0}))
    except Exception:
        return COURSES


def seed_skills():
    db = get_db()
    for name in SKILLS:
        db.skills.update_one(
            {"name": name},
            {"$setOnInsert": {"name": name, "category": SKILL_CATEGORIES.get(name, "Other")}},
            upsert=True,
        )
