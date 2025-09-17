from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="snake-query-sdk",
    version="1.0.2",
    author="Snake Query",
    author_email="info@snakequery.com",
    description="Python SDK for Snake Query API - Natural language data querying with AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://snakequery.com/",
    project_urls={
        "Bug Reports": "https://github.com/snakequery/snake-query-python-sdk/issues",
        "Source": "https://github.com/snakequery/snake-query-python-sdk/",
        "Documentation": "https://docs.snakequery.com/python-sdk",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'requests>=2.25.0',
    ],
    keywords=["snake-query", "api", "natural-language", "data-query", "ai", "sdk"],
)
