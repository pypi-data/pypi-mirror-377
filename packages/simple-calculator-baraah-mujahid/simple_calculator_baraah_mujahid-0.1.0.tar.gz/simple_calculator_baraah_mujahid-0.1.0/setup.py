from setuptools import setup, find_packages

setup(
    name="simple-calculator-baraah-mujahid",  
    version="0.1.0",
    author="Baraah Mujahed",
    author_email="your_email@example.com",
    description="A simple calculator package for basic math operations",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/simple-calculator",  
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
