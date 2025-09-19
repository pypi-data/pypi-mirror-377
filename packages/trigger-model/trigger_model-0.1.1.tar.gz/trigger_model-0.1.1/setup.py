from setuptools import setup, find_packages

setup(
    name="trigger-model",              # PyPI can have dash
    version="0.1.1",
    description="Utilities for ML models targeting hardware triggers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},           # look for packages inside src/
    packages=find_packages(where="src"),  
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
