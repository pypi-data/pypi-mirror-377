from setuptools import setup, find_packages

setup(
    name="StatsAnalyzer",
    version="0.1.0",
    description="Perform advanced statistical analysis on numerical data",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="ola al_qbita",
    author_email="you@example.com",
    packages=find_packages(),
    python_requires='>=3.13',
    license="MIT",
)
