from setuptools import setup, find_packages

setup(
    name="tmcnt",
    version="0.1",
    packages=find_packages(),
    description="program execution time count",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Arsen",
    license="MIT",
    python_requires=">=3.8",
)