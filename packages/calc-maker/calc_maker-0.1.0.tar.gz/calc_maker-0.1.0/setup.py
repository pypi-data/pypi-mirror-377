from setuptools import setup, find_packages

setup(
    name="calc_maker",
    version="0.1.0",
    packages=find_packages(),
    description="A tiny library that generates a calculator Python file",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/yourusername/calc_maker",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
