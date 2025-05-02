from setuptools import setup, find_packages

setup(
    name="dressup_ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "pillow>=9.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "python-dotenv>=0.19.0",
        "rich>=10.0.0",  # For the admin interface
        "pydantic>=2.0.0",  # For data validation
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "isort>=5.0.0",
            "mypy>=0.900",
        ]
    },
    author="DressUp AI Team",
    description="An AI-powered fashion outfit generator with personalization and A/B testing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
) 