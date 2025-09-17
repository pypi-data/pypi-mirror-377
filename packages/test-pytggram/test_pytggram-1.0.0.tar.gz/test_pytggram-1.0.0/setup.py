from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt if it exists
def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    requirements = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

# Get requirements
requirements = parse_requirements('requirements.txt')

# If requirements.txt doesn't exist or is empty, use default requirements
if not requirements:
    requirements = [
        "aiohttp>=3.8.0",
        "motor>=3.1.0",
        "redis>=4.5.0",
        "pymongo>=4.3.0",
    ]

setup(
    name="test-pytggram",
    version="1.0.0",
    author="Endtrz",
    author_email="endtrz@gmail.com",
    description="An advanced, easy-to-use Telegram Bot Framework with MongoDB support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hasnainkk-07/PyTgGram",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Communications :: Chat",
        "Topic :: Internet",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "speed": [
            "uvloop>=0.17.0",
            "aiodns>=3.0.0",
        ],
    },
    keywords="telegram bot api framework async mongodb",
    project_urls={
        "Documentation": "https://github.com/hasnainkk-07/PyTgGram/wiki",
        "Source": "https://github.com/hasnainkk-07/PyTgGram",
        "Tracker": "https://github.com/hasnainkk-07/PyTgGram/issues",
    },
    include_package_data=True,
)
