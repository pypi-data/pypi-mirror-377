from setuptools import setup, find_packages
import os

# Current directory
here = os.path.abspath(os.path.dirname(__file__))

# Long description from README
with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

# Requirements from requirements.txt
with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="xmrzapp",  # Package name on PyPI
    version="25.10.1",  # Semantic versioning
    author="rhsalisu",
    description="Extended MRZ Passport Reader From Image",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devnbugs/xmrzapp",
    project_urls={
        "Bug Tracker": "https://github.com/devnbugs/xmrzapp/issues",
    },
    packages=find_packages(include=["xmrzapp", "xmrzapp.*"]),  # Correct package name
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    extras_require={
        "cpu": ["tensorflow-cpu>=2.9.0"],
        "gpu": ["tensorflow>=2.9.0"],
    }
)
