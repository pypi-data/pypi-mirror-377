#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sellm",
    version="1.0.2",
    author="Tom Sapletta",
    author_email="info@softreck.dev",
    description="LLM-powered ProServe manifest generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tom-sapletta-com/sellm",
    py_modules=["sellm"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "pyyaml>=6.0",
        "redis>=4.0.0",
        "click>=8.0.0",
        "wmlog>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sellm=sellm:cli",
        ],
    },
)
