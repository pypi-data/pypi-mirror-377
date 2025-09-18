"""
setup.py for LLM Cost Calculator - PyPI Ready
Updated with Claude support and fixed HTML entities
"""

from setuptools import setup, find_packages
import os

def get_version():
    """Extract version from __init__.py"""
    try:
        with open("llm_cost_calculator/__init__.py", "r") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return "1.0.0"

def get_long_description():
    """Get long description from README if it exists"""
    readme_files = ["README.md", "readme.md", "README.txt", "readme.txt"]
    for readme_file in readme_files:
        if os.path.exists(readme_file):
            try:
                with open(readme_file, "r", encoding="utf-8") as f:
                    return f.read()
            except:
                pass
    return "LLM Cost Calculator - Automatic cost tracking for OpenAI, Gemini, and Claude APIs"

setup(
    # Basic package information
    name="llm-cost-calculator",
    version=get_version(),
    author="kartikeyy",
    author_email="bhalsekartikey07@gmail.com",
    description="Cost tracking for OpenAI, Gemini, and Claude APIs with session management",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/llm-cost-calculator",
    
    # Package discovery
    packages=find_packages(),
    
    # Dependencies - None required, all optional
    install_requires=[
        # No required dependencies - graceful fallbacks
    ],
    
    # Optional dependencies
    extras_require={
        'accurate': [
            'tiktoken>=0.5.0',
            'google-generativeai>=0.3.0',
            'anthropic>=0.3.0',
        ],
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
        ],
        'all': [
            'tiktoken>=0.5.0',
            'google-generativeai>=0.3.0', 
            'anthropic>=0.3.0',
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
        ],
    },
    
    # Python version requirement
    python_requires=">=3.7",
    
    # Package classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Monitoring",
    ],
    
    # Keywords for package discovery
    keywords="llm cost calculator openai gemini claude anthropic pricing tokens ai video generation",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/yourusername/llm-cost-calculator/issues",
        "Source": "https://github.com/yourusername/llm-cost-calculator",
        "Documentation": "https://github.com/yourusername/llm-cost-calculator/docs",
    },
    
    # Include package data
    include_package_data=True,
    zip_safe=False,
)
