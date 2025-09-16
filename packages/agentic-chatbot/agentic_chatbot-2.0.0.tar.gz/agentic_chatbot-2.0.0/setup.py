"""
Setup script for AI Agents Chatbot package
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
    name="agentic-chatbot",
    version="2.0.0",
    author="Dhruv Yadav",
    author_email="dhruv.y@deuexsolutions.com",  # Update with your actual email
    description="Enterprise-grade AI agents for enhanced chatbot capabilities with RAG, security, and multi-user support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/deuex-solutions/Agentic-Boilerplate",
    project_urls={
        "Bug Reports": "https://github.com/deuex-solutions/Agentic-Boilerplate/issues",
        "Source": "https://github.com/deuex-solutions/Agentic-Boilerplate",
        "Documentation": "https://github.com/deuex-solutions/Agentic-Boilerplate#readme",
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
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "demo": [
            "streamlit>=1.28.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-agents-demo=examples.streamlit_demo:main",
        ],
    },
    include_package_data=True,
    package_data={
        "agentic_chatbot": ["*.py", "**/*.py"],
    },
    keywords=[
        "ai", "agents", "chatbot", "security", "context", "model-selection",
        "openai", "gpt", "llm", "machine-learning", "nlp", "conversational-ai",
        "rag", "retrieval-augmented-generation", "enterprise", "multi-user",
        "conversation-memory", "vector-store", "chromadb", "redis", "postgresql",
        "anthropic", "claude", "google-gemini", "ollama", "langchain",
        "streaming", "async", "tools", "function-calling", "monitoring", "analytics"
    ],
    license="MIT",
    zip_safe=False,
)
