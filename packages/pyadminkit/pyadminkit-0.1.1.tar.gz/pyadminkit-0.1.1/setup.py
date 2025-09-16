from distutils.core import setup

# 版本信息
VERSION = "0.1.1"
setup(
  name = 'pyadminkit',         # How you named your package folder (MyLib)
  packages = ['pyadminkit','pyadminkit.core','pyadminkit.core.database'],   # Chose the same as "name"
  version = '0.1.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A lightweight and highly extensible Python admin system middleware',   # Give a short description about your library
  author = 'PyAdminKit Team',                   # Type in your name
  author_email = 'admin@pyadminkit.com',      # Type in your E-Mail
  url = 'https://github.com/pyadminkit/pyadminkit',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['SOME', 'MEANINGFULL', 'KEYWORDS'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
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
  python_requires=">=3.8",
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
  ],
)