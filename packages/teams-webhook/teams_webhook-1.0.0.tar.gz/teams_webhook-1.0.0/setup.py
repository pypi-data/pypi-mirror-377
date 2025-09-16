"""
Setup script for teams-webhook package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="teams-webhook",
    version="1.0.0",
    author="Pandiyaraj Karuppasamy",
    author_email="pandiyarajk@live.com",
    description="A simple Python package to send messages to Microsoft Teams using webhooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pandiyarajk/teams-webhook",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    keywords="microsoft teams webhook notification messaging",
    project_urls={
        "Bug Reports": "https://github.com/pandiyarajk/teams-webhook/issues",
        "Source": "https://github.com/pandiyarajk/teams-webhook",
        "Documentation": "https://github.com/pandiyarajk/teams-webhook#readme",
    },
)
