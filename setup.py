from codecs import open
from os import path

from setuptools import find_packages, setup
import setuptools

setuptools.setup(
    name="mlb_videos",
    project_name="mlb_videos_dev",
    version="2.0.2",
    author="Ryan Cope",
    author_email="<ryancopedev@gmail.com",
    description="<Template Setup.py package>",
    long_description="MLB Video Package",
    long_description_content_type="text/markdown",
    url="<https://github.com/authorname/templatepackage>",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
