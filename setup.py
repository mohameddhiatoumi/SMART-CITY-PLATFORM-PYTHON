"""
Setup configuration for Smart City Analytics Platform.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip()
        for line in fh
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="smart-city-platform",
    version="1.0.0",
    author="Neo-Sousse 2030 Team",
    author_email="contact@neosousse2030.tn",
    description="Smart City Analytics Platform for Neo-Sousse 2030",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neo-sousse/smart-city-platform",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "smart-city=main:cli",
        ],
    },
)
