from .skill_extractor import canonical_skill
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_jobs(user_skills, jobs, profile=None):
    user = {canonical_skill(skill).casefold() for skill in user_skills if skill.strip()}
    profile = profile or {}
    profile_details = [
        str(profile.get(field, ""))
        for field in ("education", "experience", "preferred_job_role", "preferred_location")
    ]
    profile_text = " ".join([*sorted(user), *profile_details]).strip()
    job_texts = [
        " ".join([
            job.get("title", ""),
            job.get("description", ""),
            job.get("education", ""),
            job.get("experience", ""),
            job.get("location", ""),
            " ".join(job.get("required_skills", [])),
            " ".join(job.get("preferred_skills", [])),
        ])
        for job in jobs
    ]
    similarities = [0.0] * len(jobs)
    if profile_text.strip() and any(text.strip() for text in job_texts):
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        vectors = vectorizer.fit_transform([profile_text, *job_texts])
        similarities = cosine_similarity(vectors[0:1], vectors[1:]).ravel().tolist()

    result = []
    for job, similarity in zip(jobs, similarities):
        required_list = list(dict.fromkeys(job.get("required_skills", [])))
        required = {canonical_skill(skill).casefold() for skill in required_list}
        matched = [skill for skill in required_list if canonical_skill(skill).casefold() in user]
        missing = [skill for skill in required_list if canonical_skill(skill).casefold() not in user]
        coverage = len(matched) / len(required_list) if required_list else 0
        final = round((0.75 * coverage + 0.25 * similarity) * 100, 1)
        result.append({
            "job_id": job["job_id"],
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "match_percentage": final,
            "skill_match_percentage": round(coverage * 100, 1),
            "content_similarity": round(similarity, 4),
            "matched_skills": matched,
            "missing_skills": missing,
            "required_skills": required_list,
        })
    return sorted(result, key=lambda item: (-item["match_percentage"], item["job_id"]))
