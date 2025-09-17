from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="manifold_fabric_utils",
    version="0.1.0",
    packages=find_packages(),
    author="Patrick Dwyer",
    author_email="patrick.dwyer@manifold.group",
    description="Utilities for Fabric/Spark environments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    url="https://bitbucket.org/digintent/fabric-utils/src",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)