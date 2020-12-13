import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="fasteve",
    version="0.1.2",
    description="A simple and feature complete REST API framework designed for speed.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Wytamma/fasteve",
    author="Wytamma Wirth",
    author_email="wytamma.wirth@me.com",
    license="BSD",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=find_packages(exclude=("tests",)),
    install_requires=["fastapi", "uvicorn", "motor", "email-validator"],
)