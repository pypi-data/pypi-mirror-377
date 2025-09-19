from setuptools import setup, find_packages

setup(
    name="trigger_model",
    version="0.1.0",
    description="Utilities for ML models targeting hardware triggers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@cern.ch",
    url="https://github.com/your-repo/trigger_model_pkg",
    packages=find_packages(),
    install_requires=[
        "mlflow>=2.0",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
