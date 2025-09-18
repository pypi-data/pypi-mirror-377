from setuptools import setup, find_packages
import os

setup(
    name="gommit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gommit=gommit.gommit:main",
        ],
    },
    author="Mostafa Motahari",
    author_email="mostafamotahari2004@gmail.com",
    description="Generate Git commit messages using an OpenAI-compatible API",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/MostafaMotahari/gommit",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
