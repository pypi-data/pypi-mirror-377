"""
Setup configuration for the fileorganizer package.
"""

from setuptools import setup, find_packages

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Package metadata
setup(
    name="fileorganizer-farhan",
    version="0.1.0",
    author="Farhan Ahmad",
    author_email="farhanbangash091@gmail.com",
    description="A tool to organize messy files into categorized folders",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FarhanAhmad/fileorganizer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "fileorganizer=fileorganizer.cli:main",
        ],
    },
    keywords="file organization, cleanup, automation",
)