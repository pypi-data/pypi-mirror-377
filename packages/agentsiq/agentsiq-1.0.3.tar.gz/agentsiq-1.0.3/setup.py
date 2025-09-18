#!/usr/bin/env python3
"""
AgentsIQ Setup Script
Intelligent Multi-Model Router for LLM Selection
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="agentsiq",
    version="1.0.3",
    author="AgentsIQ Team",
    author_email="team@agentsiq.ai",
    description="Intelligent Multi-Model Router for LLM Selection",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AgentsIQ",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/AgentsIQ/issues",
        "Source": "https://github.com/yourusername/AgentsIQ",
        "Documentation": "https://github.com/yourusername/AgentsIQ/blob/main/docs/architecture.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentsiq-benchmark=examples.benchmark:run",
            "agentsiq-demo=examples.serve_and_demo:main",
        ],
    },
    include_package_data=True,
    package_data={
        "agentsiq": ["*.yaml", "*.yml"],
    },
    keywords=[
        "ai", "llm", "router", "multi-model", "intelligent", "selection",
        "openai", "anthropic", "google", "ollama", "grok", "optimization",
        "cost-effective", "performance", "analytics", "agentops"
    ],
    zip_safe=False,
)
