from setuptools import setup, find_packages

setup(
    name="gemini-parallel",
    version="0.1.0",
    description="Parallel Gemini API calls with MongoDB logging",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "google-genai",
        "motor",
        "pydantic",
        "tqdm",
        "python-dotenv",
        "pillow",
        "pymongo"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)