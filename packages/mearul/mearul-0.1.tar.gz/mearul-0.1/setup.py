
from setuptools import setup, find_packages

setup(
    name="mearul",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "cryptography",
    ],
    python_requires=">=3.8",
    author="Justin",
    author_email="me@dev.org",
    description="Fully hidden Python package for Jupyter Notebook",
    # Removed long_description to avoid build error due to missing README.md
    # long_description=open("README.md").read(),
    # long_description_content_type="text/markdown",
    url="https://github.com/yourgithub/mearul_package_final",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
