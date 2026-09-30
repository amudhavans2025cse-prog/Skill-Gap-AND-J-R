from .skill_extractor import canonical_skill


def norm(skill):
    return canonical_skill(skill).casefold()

def skill_gap(user_skills, required_skills):
    user = {norm(x) for x in user_skills}
    required_map = {}
    for skill in required_skills:
        required_map.setdefault(norm(skill), skill)
    matched = [v for k, v in required_map.items() if k in user]
    missing = [v for k, v in required_map.items() if k not in user]
    score = round(len(matched) / len(required_map) * 100, 1) if required_map else 0
    return {
        "match_percentage": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "required_skills": list(required_map.values())
    }


def build_roadmap(user_skills, required_skills):
    gaps = skill_gap(user_skills, required_skills)["missing_skills"]
    resources = {
        "Python": ("Python tutorial", "https://docs.python.org/3/tutorial/"),
        "SQL": ("SQL tutorial", "https://www.postgresql.org/docs/current/tutorial.html"),
        "Git": ("Git book", "https://git-scm.com/book/en/v2"),
        "JavaScript": ("JavaScript guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"),
        "React": ("React documentation", "https://react.dev/learn"),
        "FastAPI": ("FastAPI tutorial", "https://fastapi.tiangolo.com/tutorial/"),
        "Machine Learning": ("Scikit-learn tutorials", "https://scikit-learn.org/stable/tutorial/index.html"),
        "Docker": ("Docker getting started", "https://docs.docker.com/get-started/"),
    }
    return {
        "steps": [
            {
                "order": index,
                "skill": skill,
                "duration_weeks": 1,
                "focus": f"Learn the fundamentals of {skill} and complete one small hands-on exercise.",
                "resource_title": resources.get(skill, (f"{skill} learning path", ""))[0],
                "resource_url": resources.get(skill, ("", ""))[1],
            }
            for index, skill in enumerate(gaps, start=1)
        ],
        "total_weeks": len(gaps),
    }
