import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

version = os.environ.get("VERSION", "v0.0.1")

setuptools.setup(
    name="components", # Replace with your own username
    version=str(version),
    author="JoeyDP",
    author_email="joeydepauw@gmail.com",
    description="Python library to facilitate modular components that can be combined through dependency injection.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
) 
