# setup.py

from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bodewell-ui-py",
    version="0.1.0",
    author="Bodewell",
    author_email="contact@bodewell.io",
    description="A themed component library for building Bodewell apps with Python and Dash.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bodewell-io/bodewell-ui-py", # This will be our new repo URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    # Define the dependencies required for our library to work
    install_requires=[
        "dash>=2.0.0",
        "dash-mantine-components>=0.12.1" # We depend on the original library
    ],
)