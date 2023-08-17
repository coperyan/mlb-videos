# Always prefer setuptools over distutils
# To use a consistent encoding
from codecs import open
from os import path

from setuptools import find_packages, setup

vrsn_file = path.join(path.abspath(path.dirname(__file__)), "mlb_videos", "version.py")
with open(vrsn_file, encoding="utf-8") as f:
    version = f.read().split(" = ")[-1].strip('"')


setup(
    name="mlb_videos",
    project_name="mlb_videos",
    version=version,
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