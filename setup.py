# Always prefer setuptools over distutils
# To use a consistent encoding
from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Get Version
version_file = path.join(here, "mlb_videos", "version.py")
with open(version_file, encoding="utf-8") as f:
    version = f.read().split(" = ")[-1].strip().strip('"')

setup(
    name="mlb_videos",
    project_name="mlb_videos",
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,
    description="Gather, analyze & create videos from Baseball data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # The project's main homepage.
    url="https://github.com/coperyan/mlb_videos",
    # Author details
    author="Ryan Cope",
    author_email="ryancopedev@gmail.com",
    # Maintainer
    maintainer="Moshe Schorr",
    # Choose your license
    license="MIT",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    # What does your project relate to?
    keywords="baseball videos web scraping youtube compilations statistics",
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=["tests", "tests.*"]),
    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        "ffmpeg_python>=0.2.0"
        "google_api_python_client>=2.93.0"
        "httplib2>=0.20.4"
        "moviepy>=1.0.3"
        "oauth2client>=4.1.3"
        "pandas>=1.4.3"
        "python_dateutil>=2.8.2"
        "requests>=2.31.0"
        "swifter>=1.3.4"
        "tqdm>=4.64.0"
    ],
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     #    'dev': ['check-manifest'],
    #     "test": [
    #         "pytest>=6.0.2",
    #         "mypy>=0.782",
    #         "pytest-cov>=2.10.1",
    #         "pytest-xdist>=2.1.0",
    #         "types-requests>=2.18.1",
    #     ],
    # },
    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    include_package_data=True,
    # package_data={
    #    'sample': ['package_data.dat'],
    # },
    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    # },
)
