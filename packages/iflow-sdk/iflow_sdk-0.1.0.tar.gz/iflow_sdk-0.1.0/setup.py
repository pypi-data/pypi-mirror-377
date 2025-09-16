"""Setup configuration for iFlow SDK."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme = Path("README.md").read_text(encoding="utf-8")

# Read requirements
requirements = Path("requirements.txt").read_text().splitlines()
requirements = [r for r in requirements if r and not r.startswith("#")]

setup(
    name="iflow-cli-sdk",
    version="0.1.0",
    author="iFlow Team",
    author_email="team@iflow.dev",
    description="Python SDK for iFlow CLI - Build AI-powered applications with the Agent Communication Protocol",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/iflow-cli-sdk-python",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/iflow-cli-sdk-python/issues",
        "Documentation": "https://github.com/yourusername/iflow-cli-sdk-python/blob/main/README.md",
        "Source Code": "https://github.com/yourusername/iflow-cli-sdk-python",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "isort>=5.13.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "types-aiofiles>=23.2.0",
        ],
        "docs": [
            "sphinx>=4.5.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    keywords=[
        "iflow",
        "ai",
        "agent",
        "llm",
        "cli",
        "acp",
        "websocket",
        "async",
        "sdk",
        "api",
        "chatbot",
        "automation",
    ],
)