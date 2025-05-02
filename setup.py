from setuptools import setup, find_packages

setup(
    name="dressup_ai",
    version="0.1.0",
    description="AI-powered fashion outfit generator with personalization and style validation",
    author="DressUp AI Team",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "pillow>=10.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "rich>=13.0.0",
        "typer>=0.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ]
    },
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "dressup=dressup_ai.cli:main",
            "dressup-admin=dressup_ai.admin:main",
        ]
    },
) 