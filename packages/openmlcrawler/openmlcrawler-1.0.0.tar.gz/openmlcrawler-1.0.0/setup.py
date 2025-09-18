"""
Setup script for openmlcrawler.
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt if it exists."""
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="openmlcrawler",
    version="1.0.0",
    author="Krishna Bajpai, Vedanshi Gupta",
    author_email="krishna@krishnabajpai.me",
    description="A unified framework for crawling and preparing ML-ready datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/krish567366/openmlcrawler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements() or [
        "pandas>=1.3.0",
        "requests>=2.25.0",
        "numpy>=1.20.0",
        "scikit-learn>=1.0.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
        "pyarrow>=6.0.0",
        "nltk>=3.6.0",
        "pdfplumber>=0.6.0",
        "aiohttp>=3.8.0",
        "playwright>=1.20.0",
        "typer>=0.4.0",
        "rich>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.900",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "nlp": [
            "transformers>=4.0.0",
            "torch>=1.9.0",
            "datasets>=1.0.0",
        ],
        "async": [
            "aiofiles>=0.7.0",
            "asyncio-throttle>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openmlcrawler=openmlcrawler.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "openmlcrawler": ["config/*.yaml", "config/*.json"],
    },
    zip_safe=False,
)