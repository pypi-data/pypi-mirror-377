#!/usr/bin/env python3
"""
Setup script for Snowflake Connector Helper
Internal package for Team of Noah A from SignifyHealth

INTERNAL USE ONLY
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="snowflake-connector-helper",
    version="1.0.0",
    author="Team of Noah A - SignifyHealth",
    description="Internal Snowflake connector with PKCS#8 authentication for SignifyHealth Team",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=[
        "snowflake-connector-python>=3.0.0",
        "pandas>=1.5.0",
        "pydantic>=1.10.0",
        "python-dotenv>=0.19.0",
        "cryptography>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "secrets": [
            "boto3>=1.26.0",
            "hvac>=1.0.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    # Internal use metadata
    keywords="snowflake database internal signifyhealth noah-a pkcs8",
)