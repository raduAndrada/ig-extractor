#!/usr/bin/env python3
"""Setup script to create project directory structure."""
import os
from pathlib import Path

# Define project structure
directories = [
    "app/static/css",
    "app/static/js",
    "app/static/images",
    "app/templates",
    "app/models",
    "app/services",
    "app/routes",
    "data/thumbnails",
    "tests",
]

# Create all directories
for directory in directories:
    Path(directory).mkdir(parents=True, exist_ok=True)
    print(f"✓ Created: {directory}/")

# Create __init__.py files for Python packages
init_files = [
    "app/models/__init__.py",
    "app/services/__init__.py",
    "app/routes/__init__.py",
    "tests/__init__.py",
]

for init_file in init_files:
    Path(init_file).touch()
    print(f"✓ Created: {init_file}")

print("\n✅ Project structure created successfully!")
print("\nDirectory tree:")
print("""
ig-extractor/
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/
├── data/
│   └── thumbnails/
├── tests/
├── .env.example
├── .gitignore
├── config.py
├── README.md
├── requirements.txt
└── run.py
""")

print("\nNext steps:")
print("1. Activate virtual environment: source .venv/bin/activate")
print("2. Install dependencies: pip install -r requirements.txt")
print("3. Copy .env.example to .env and configure")
