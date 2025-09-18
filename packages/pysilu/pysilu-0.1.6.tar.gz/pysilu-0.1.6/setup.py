from setuptools import setup, find_packages

setup(
    name="silu",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "silu=silu.__main__:main",
        ],
    },
    install_requires=[
        # Add any dependencies here
    ],
    author="askender",
    author_email="askender43@gmail.com",
    description="A simple AI programming language",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/askender/silu",  # Replace with your repo URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
