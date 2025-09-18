from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitfind",
    version="0.1.1",
    author="Naman Katare",
    author_email="katare272004gmail.com",
    description="A Python package to find and analyze GitHub repository statistics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/27Naman2004/gitfind",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "colorama>=0.4.0"
    ],
    entry_points={
        "console_scripts": [
            "gitfind=gitfind.cli:main",
        ],
    },
    include_package_data=True,
)