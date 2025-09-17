"""
Setup script for the Revo library.
This provides backward compatibility for pip install -e .
"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="revo",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python library for Apollo API authentication and LangChain-based LLM tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/revo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=[
        "requests>=2.31.0",
        "httpx>=0.24.0",
        "httpx-auth>=1.0.0",
        "langchain-core>=0.1.0",
        "langchain-openai>=0.1.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="apollo llm langchain authentication token-management",
    include_package_data=True,
    zip_safe=False,
)
