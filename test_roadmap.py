from ai_modules.roadmap_generator import generate_roadmap

roadmap = generate_roadmap(
    "python developer"
)

for step in roadmap:
    print(step)