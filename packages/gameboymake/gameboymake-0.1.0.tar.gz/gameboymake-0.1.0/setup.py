# setup.py
from setuptools import setup, find_packages

setup(
    name="gameboymake",
    version="0.1.0",
    description="Python library to develop Game Boy games and generate ROMs",
    long_description="",  # No README.md
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="youremail@example.com",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
)
