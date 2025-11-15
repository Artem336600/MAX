from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eidos-sdk",
    version="0.1.0",
    author="Eidos Team",
    author_email="team@eidos.dev",
    description="Python SDK для создания модулей Eidos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eidos/eidos-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
    ],
)
