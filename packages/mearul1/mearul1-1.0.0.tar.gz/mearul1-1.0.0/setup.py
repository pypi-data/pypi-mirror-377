from setuptools import setup, find_packages

setup(
    name="mearul1",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "cryptography"
    ],
    author="Justin Mearul",
    author_email="yoyoyo@gmail.com",
    description="Encrypted Python files package for Jupyter Notebook",
    python_requires='>=3.8',
)
