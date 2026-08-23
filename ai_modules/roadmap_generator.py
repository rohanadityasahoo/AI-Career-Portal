def generate_roadmap(career):
    roadmaps = {
        "python developer": [
            "Learn Python Basics",
            "Learn OOP",
            "Learn Flask/Django",
            "Learn MySQL",
            "Build Projects",
            "Learn Git & GitHub",
            "Apply for Internships"
        ],

        "data scientist": [
            "Learn Python",
            "Learn NumPy",
            "Learn Pandas",
            "Learn Machine Learning",
            "Learn Data Visualization",
            "Build ML Projects",
            "Apply for Data Science Roles"
        ],

        "software engineer": [
            "Learn Programming",
            "Learn DSA",
            "Learn Databases",
            "Learn Web Development",
            "Build Projects",
            "Practice Coding Interviews",
            "Apply for Jobs"
        ]
    }

    return roadmaps.get(
        career.lower(),
        ["Roadmap not available"]
    )