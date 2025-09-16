"""Setup configuration for QATest package."""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="qatest",
    version="1.0.1",
    author="QATest Team",
    author_email="",
    description="Test case management tool for uploading JSON test cases to QATest",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/qatest-cli",
    packages=find_packages(exclude=["tests*", "example*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "qatest=qatest.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="testing qa test-cases test-management json-upload",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/qatest-cli/issues",
        "Source": "https://github.com/yourusername/qatest-cli",
    },
)
