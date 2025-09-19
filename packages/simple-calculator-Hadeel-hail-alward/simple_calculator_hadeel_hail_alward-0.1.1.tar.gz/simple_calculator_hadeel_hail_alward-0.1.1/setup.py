from setuptools import setup, find_packages

setup(
    name="simple-calculator-Hadeel-hail-alward", 
    version="0.1.1", 
    author="Hadeel-hail",
    description="A simple calculator package for basic arithmetic operations",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/simple-calculator-Ayah-Alheilah/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
