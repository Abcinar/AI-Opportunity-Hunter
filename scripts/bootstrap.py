from pathlib import Path

STRUCTURE = {
    "engine/intelligence": [
        "__init__.py",
        "base_engine.py",
        "contracts.py",
        "constants.py",
        "taxonomy.py",
        "weights.py",
        "category_engine.py",
        "score_engine.py",
        "confidence_engine.py",
        "founder_fit_engine.py",
        "recommendation_engine.py",
    ]
}

for folder, files in STRUCTURE.items():
    path = Path(folder)
    path.mkdir(parents=True, exist_ok=True)

    for file in files:
        target = path / file
        target.touch(exist_ok=True)
        print(f"✔ {target}")

print("\n✅ OIP Architecture Bootstrapped")
