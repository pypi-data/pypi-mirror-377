#!/usr/bin/env python3
"""
Setup script for video-transcription-agent package.
"""

from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-agent-video-transcription",
    version="1.1.2",
    author="Lopand Solutions",
    author_email="contact@lopand.com",
    maintainer="Paulo Cesar Andrade Gonzalez",
    maintainer_email="paulocesarandradegonzalez@lopand.com",
    description="Multi-agent AI system for video transcription using LangChain and AutoGen",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lopand-solutions/video-transcription-agent",
    project_urls={
        "Bug Reports": "https://github.com/lopand-solutions/video-transcription-agent/issues",
        "Source": "https://github.com/lopand-solutions/video-transcription-agent",
        "Documentation": "https://github.com/lopand-solutions/video-transcription-agent#readme",
    },
    packages=find_packages(where="src"),
    py_modules=["main"],
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "pre-commit>=3.6.0",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "video-transcription-agent=main:main",
            "vt-agent=main:main",
            "vt-cli=cli.interactive_cli:main",
        ],
    },
    keywords=[
        "video", "transcription", "ai", "agents", "langchain", "autogen",
        "whisper", "multimedia", "speech-recognition", "nlp"
    ],
    include_package_data=True,
    zip_safe=False,
)
