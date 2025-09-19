from setuptools import setup, find_packages

setup(
    name="mintzy",
    version="0.1.1",
    description="Mintzy SDK for stock price prediction",
    author="Om Kulthe ",
    author_email="mintzy01.ai@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
