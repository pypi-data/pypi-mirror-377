# minitorch_v2/setup.py
from setuptools import setup, find_packages

setup(
    name="minitorch",
    version="0.1.0",
    description="A lightweight machine learning library inspired by PyTorch",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="gantengiyaz6@gmail.com",
    packages=find_packages(include=["minitorch", "torch.*"]),
    install_requires=[
        "numpy>=1.21.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    include_package_data=True,
)

