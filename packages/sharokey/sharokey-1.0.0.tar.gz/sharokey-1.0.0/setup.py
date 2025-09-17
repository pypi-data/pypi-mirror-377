from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sharokey",
    version="1.0.0",
    author="Sharokey Team",
    author_email="support@sharokey.com",
    description="Sharokey Python SDK for secure secret sharing with Zero Knowledge encryption",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sharokey/python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.8.0,<4.0.0",
        "aiofiles>=23.0.0,<25.0.0",
        "cryptography>=41.0.0,<43.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0,<9.0.0",
            "pytest-asyncio>=0.21.0,<1.0.0",
            "pytest-cov>=4.0.0,<6.0.0",
            "black>=23.0.0,<25.0.0",
            "isort>=5.12.0,<6.0.0",
            "mypy>=1.5.0,<2.0.0",
            "flake8>=6.0.0,<8.0.0",
        ],
    },
    # No CLI entry points - this is a library only
    keywords="secrets, encryption, security, zero-knowledge, api, sharokey",
    project_urls={
        "Bug Reports": "https://github.com/sharokey/python-sdk/issues",
        "Documentation": "https://docs.sharokey.com/python",
        "Source": "https://github.com/sharokey/python-sdk",
    },
)