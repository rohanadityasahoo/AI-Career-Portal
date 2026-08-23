from ai_modules.job_recommender import recommend_jobs

skills = [
    "python",
    "flask",
    "mysql",
    "git"
]

jobs = recommend_jobs(skills)

print("Recommended Jobs:")
for job in jobs:
    print("-", job)