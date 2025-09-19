from setuptools import setup, find_packages

setup(
    name="groq-eval-score",  # must be unique on PyPI
    version="0.1.0",
    description="A package to evaluate output relevancy using Groq LLM",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Syed Farith C",
    author_email="syedfarith1351@gmail.com",
    packages=find_packages(),
    install_requires=["groq"],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
