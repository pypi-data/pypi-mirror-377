from setuptools import setup, find_packages

setup(
    name="pyspark_data_prep",
    version="1.0.0",
    description="A utility library for modifying PySpark DataFrames.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Lingesh G",
    author_email="lingeshg.dev@gmail.com",
    url="https://github.com/githubLINGESH/pyspark_data_prep",
    packages=find_packages(),
    install_requires=[
        "pyspark>=3.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
