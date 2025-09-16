"""
PyAdminKit setup script for PyPI distribution
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements
def read_requirements():
    requirements = []
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
    return requirements

# 版本信息
VERSION = "0.1.3"

setup(
    name="pyadminkit",
    version="0.1.3",
    author="PyAdminKit Team",
    author_email="admin@pyadminkit.com",
    description="A lightweight and highly extensible Python admin system middleware",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pyadminkit/pyadminkit",
    project_urls={
        "Documentation": "https://pyadminkit.readthedocs.io/",
        "Source Code": "https://github.com/pyadminkit/pyadminkit",
        "Bug Reports": "https://github.com/pyadminkit/pyadminkit/issues",
        "Changelog": "https://github.com/pyadminkit/pyadminkit/blob/main/CHANGELOG.md",
    },
    packages=['pyadminkit','pyadminkit.core','pyadminkit.core.database'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Framework :: FastAPI",
        "Framework :: Flask",
        "Framework :: Django",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "mysql": ["aiomysql>=0.2.0"],
        "postgresql": ["asyncpg>=0.28.0"],
        "sqlite": ["aiosqlite>=0.19.0"],
        "mongodb": ["motor>=3.3.0"],
        "fastapi": ["fastapi>=0.100.0"],
        "flask": ["flask>=2.0.0"],
        "django": ["django>=4.0.0"],
        "full": [
            "aiomysql>=0.2.0",
            "asyncpg>=0.28.0", 
            "aiosqlite>=0.19.0",
            "motor>=3.3.0",
            "fastapi>=0.100.0",
            "flask>=2.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.0.0",
        ],
    },
    keywords=[
        "admin", "dashboard", "cms", "management", "database", "orm",
        "fastapi", "flask", "django", "async", "mysql", "postgresql",
        "sqlite", "mongodb", "crud", "api", "web", "framework"
    ],
    zip_safe=False,
)
