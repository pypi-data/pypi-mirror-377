#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mr-studydev",  # Using mr-studydev to match your GitHub repo
    version="1.0.0",
    author="PrinceTheProgrammer",
    author_email="princetheprogrammer@example.com",
    description="🎯 Ultimate Student & Developer Productivity CLI Tool with Pomodoro, Projects & Study Materials",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/the-ai-developer/mr.studydev",
    project_urls={
        "Bug Reports": "https://github.com/the-ai-developer/mr.studydev/issues",
        "Source": "https://github.com/the-ai-developer/mr.studydev",
        "Documentation": "https://github.com/the-ai-developer/mr.studydev#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Software Development",
        "Topic :: System :: Shells",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    keywords="productivity, pomodoro, cli, study, project-management, flashcards, terminal, developer-tools, student-tools, time-management",
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "studydev=studydev.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
