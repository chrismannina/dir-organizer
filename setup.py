#!/usr/bin/env python3
"""
Setup script for the LLM Directory Organizer package.
"""

from setuptools import find_packages, setup

setup(
    name="llm-organizer",
    version="0.1.0",
    description="AI-powered directory organization tool",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/llm-directory-organizer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "llama-index>=0.7.0",
        "pydantic>=2.0.0",
        "openai>=1.0.0",
        "python-dotenv>=0.19.0",
        "pyyaml>=6.0",
        "python-docx>=0.8.11",
        "PyPDF2>=3.0.0",
        "python-magic>=0.4.24",
        "tqdm>=4.64.0",
    ],
    entry_points={
        "console_scripts": [
            "llm-organizer=llm_organizer.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities",
    ],
)
