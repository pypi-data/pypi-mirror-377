from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    page_description = f.read()

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="package_histmatch",
    version="0.0.1",
    author="Nayara",
    author_email="nayara_franco_almeida@hotmail.com",
    description="My short description",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nayarah/simple-package-template.git",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
)
