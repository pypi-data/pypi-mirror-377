"""
Setup configuration for tensorchat-streaming Python package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tensorchat-streaming",
    version="1.0.1",
    author="Tensorchat.io",
    author_email="support@tensorchat.io",
    description="Framework-agnostic Python client for Tensorchat.io streaming API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/datacorridor/tensorchat-streaming",
    project_urls={
        "Bug Tracker": "https://github.com/datacorridor/tensorchat-streaming/issues",
        "Documentation": "https://tensorchat.io/docs",
        "Homepage": "https://tensorchat.io",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "dataclasses; python_version<'3.7'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "pre-commit>=2.20.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
        ],
    },
    keywords=[
        "tensorchat",
        "streaming",
        "ai",
        "real-time",
        "llm",
        "async",
        "python",
        "openrouter",
        "concurrent",
    ],
    include_package_data=True,
    zip_safe=False,
)