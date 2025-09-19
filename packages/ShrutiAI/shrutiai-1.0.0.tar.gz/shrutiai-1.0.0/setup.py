"""
Setup script for ShrutiAI SDK
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements if file exists
def read_requirements():
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return ["requests>=2.25.0"]

setup(
    name="ShrutiAI",
    version="1.0.0",
    author="Shri Sai Technology",
    author_email="support@sstus.net",
    description="Python SDK for interacting with the shrutiAI API - your AI-powered assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shrisai-tech/shruti-ai-sdk",
    project_urls={
        "Homepage": "https://shruti.ai/",
        "Documentation": "https://shruti.ai/docs",
        "Repository": "https://github.com/shrisai-tech/shruti-ai-sdk",
        "Bug Reports": "https://github.com/shrisai-tech/shruti-ai-sdk/issues",
        "Support": "mailto:support@sstus.net",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    keywords=[
        "ai",
        "chat",
        "assistant",
        "api",
        "sdk",
        "shruti",
        "artificial-intelligence",
        "chatbot",
        "voice",
        "location",
        "otp",
        "verification",
        "image-analysis",
        "document-processing",
        "farming",
        "travel",
        "math",
        "search",
        "youtube"
    ],
    package_data={
        "ShrutiAI": ["*.py"],
    },
    include_package_data=True,
    zip_safe=False,
)
