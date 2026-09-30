import asyncio
import os
from io import BytesIO
import unittest
from unittest.mock import patch, Mock

from fastapi import UploadFile
import jwt

from app import main as api
from app.auth import create_access_token, hash_password, verify_password
from app.ml.job_recommender import recommend_jobs
from app.ml.skill_extractor import extract_skills
from app.ml.skill_gap import build_roadmap, skill_gap
from app.seed import COURSES, JOBS


class SkillFeatureTests(unittest.TestCase):
    def test_resume_extraction_recognizes_common_aliases(self):
        skills = extract_skills(b"Built APIs with Python, JS, sklearn, and ML.", "resume.txt")

        self.assertEqual(skills, ["Python", "JavaScript", "Machine Learning", "Scikit-learn"])

    def test_c_and_cpp_remain_distinct(self):
        self.assertEqual(extract_skills(b"Used C++ and C in coursework.", "resume.txt"), ["C", "C++"])
        self.assertEqual(skill_gap(["C++"], ["C++", "C"])["matched_skills"], ["C++"])

    def test_skill_gap_is_normalized_and_deduplicated(self):
        result = skill_gap(["js", "Python"], ["JavaScript", "Python", "Python", "SQL"])

        self.assertEqual(result["match_percentage"], 66.7)
        self.assertEqual(result["matched_skills"], ["JavaScript", "Python"])
        self.assertEqual(result["missing_skills"], ["SQL"])

    def test_recommendations_are_explainable_and_stably_ranked(self):
        jobs = [
            {"job_id": "B", "title": "Backend", "company": "B Co", "location": "Remote", "required_skills": ["Python", "SQL"]},
            {"job_id": "A", "title": "Analyst", "company": "A Co", "location": "Remote", "required_skills": ["Python", "SQL"]},
            {"job_id": "C", "title": "Designer", "company": "C Co", "location": "Remote", "required_skills": ["CSS"]},
        ]

        first = recommend_jobs(["Python", "SQL"], jobs)
        second = recommend_jobs(["Python", "SQL"], jobs)

        self.assertEqual(first, second)
        self.assertEqual([job["job_id"] for job in first], ["A", "B", "C"])
        self.assertEqual(first[0]["matched_skills"], ["Python", "SQL"])
        self.assertEqual(first[2]["missing_skills"], ["CSS"])

    def test_recommendations_use_description_similarity_when_skill_coverage_ties(self):
        jobs = [
            {
                "job_id": "B",
                "title": "Python Developer",
                "company": "B Co",
                "location": "Remote",
                "description": "Build general purpose software services.",
                "required_skills": ["Python"],
            },
            {
                "job_id": "A",
                "title": "Data Analyst",
                "company": "A Co",
                "location": "Remote",
                "description": "Analyze datasets with Pandas and Python to create statistical reports.",
                "required_skills": ["Python"],
            },
        ]

        recommendations = recommend_jobs(["Python", "Pandas", "Statistics"], jobs)

        self.assertEqual(recommendations[0]["job_id"], "A")
        self.assertEqual(recommendations[0]["skill_match_percentage"], 100)
        self.assertGreater(recommendations[0]["content_similarity"], recommendations[1]["content_similarity"])

    def test_recommendations_use_saved_role_and_location_preferences(self):
        jobs = [
            {"job_id": "B", "title": "Python Developer", "company": "B Co", "location": "Mumbai", "description": "Develop cloud services.", "education": "B.Tech", "experience": "0-2 years", "required_skills": ["Python"]},
            {"job_id": "A", "title": "Data Analyst", "company": "A Co", "location": "Chennai", "description": "Analyze business reports.", "education": "B.Tech", "experience": "0-2 years", "required_skills": ["Python"]},
        ]

        recommendations = recommend_jobs(
            ["Python"], jobs,
            {"education": "B.Tech", "experience": "1 year", "preferred_job_role": "Data Analyst", "preferred_location": "Chennai"},
        )

        self.assertEqual(recommendations[0]["job_id"], "A")

    def test_roadmap_contains_only_missing_skills_in_requirement_order(self):
        roadmap = build_roadmap(["Python", "git"], ["Python", "SQL", "Git"])

        self.assertEqual(roadmap["total_weeks"], 1)
        self.assertEqual([step["skill"] for step in roadmap["steps"]], ["SQL"])
        self.assertTrue(roadmap["steps"][0]["resource_url"].startswith("https://"))

    def test_api_analysis_recommendation_roadmap_and_resume_upload(self):
        jobs = [{
            "job_id": "JOB001",
            "title": "Python Developer",
            "company": "DemoTech",
            "location": "Bengaluru",
            "description": "Build APIs",
            "required_skills": ["Python", "FastAPI", "SQL"],
        }]

        with patch("app.main.get_jobs", return_value={"jobs": jobs}):
            analysis = api.analyze(api.AnalyzeRequest(skills=["Python"], job_id="JOB001"))
            recommendations = api.recommend(api.RecommendRequest(skills=["Python"]))
            roadmap = api.roadmap(api.RoadmapRequest(skills=["Python"], job_id="JOB001"))
            resume = asyncio.run(api.resume_skills(UploadFile(
                file=BytesIO(b"Python, JS, and Git"), filename="resume.txt"
            )))

        self.assertEqual(analysis["missing_skills"], ["FastAPI", "SQL"])
        self.assertEqual(recommendations["recommendations"][0]["job_id"], "JOB001")
        self.assertEqual([step["skill"] for step in roadmap["steps"]], ["FastAPI", "SQL"])
        self.assertEqual(resume["skills"], ["Python", "JavaScript", "Git"])

    def test_auth_hashes_passwords_and_signs_role_scoped_tokens(self):
        with patch.dict(os.environ, {"JWT_SECRET_KEY": "test-key-that-is-only-used-in-tests"}):
            password_hash = hash_password("correct horse battery staple")
            token = create_access_token("arun@example.com", "student")
            claims = jwt.decode(token, "test-key-that-is-only-used-in-tests", algorithms=["HS256"])

        self.assertNotEqual(password_hash, "correct horse battery staple")
        self.assertTrue(verify_password("correct horse battery staple", password_hash))
        self.assertFalse(verify_password("wrong password", password_hash))
        self.assertEqual(claims["sub"], "arun@example.com")
        self.assertEqual(claims["role"], "student")

    def test_register_and_login_store_only_password_hash(self):
        db = Mock()
        db.users.find_one.return_value = {
            "email": "arun@example.com",
            "role": "student",
            "password_hash": hash_password("password-123"),
        }
        with patch.dict(os.environ, {"JWT_SECRET_KEY": "test-key-that-is-only-used-in-tests"}):
            with patch("app.main.get_db", return_value=db):
                registered = api.register(api.RegisterRequest(
                    name="Arun Kumar", email=" Arun@Example.com ", password="password-123"
                ))
                logged_in = api.login(api.LoginRequest(email="arun@example.com", password="password-123"))

        inserted_user = db.users.insert_one.call_args.args[0]
        self.assertEqual(inserted_user["email"], "arun@example.com")
        self.assertEqual(inserted_user["role"], "student")
        self.assertNotEqual(inserted_user["password_hash"], "password-123")
        self.assertEqual(registered["token_type"], "bearer")
        self.assertEqual(logged_in["role"], "student")

    def test_demo_seed_and_required_api_routes(self):
        self.assertGreaterEqual(len(JOBS), 30)
        self.assertTrue(all(job.get("salary_range") and job.get("employment_type") for job in JOBS))
        self.assertGreaterEqual(len(COURSES), 12)
        recommended = api.recommended_courses(["Python"])["courses"]
        self.assertNotIn("Python", [course["skill"] for course in recommended])
        paths = {route.path for route in api.app.routes}
        self.assertTrue({
            "/api/auth/register", "/api/auth/login", "/api/profile",
            "/api/admin/jobs", "/api/admin/skills", "/api/skills", "/api/admin/courses",
            "/api/resume/upload",
            "/api/recommendations/jobs", "/api/roadmap/generate",
        } <= paths)


if __name__ == "__main__":
    unittest.main()