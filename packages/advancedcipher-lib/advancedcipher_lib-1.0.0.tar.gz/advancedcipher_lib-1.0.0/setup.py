
from setuptools import setup, find_packages

setup(
    name="advancedcipher_lib",  
    version="1.0.0",
    author="Ali Alsheikh",
    author_email="ali453345ali@gmail.com",
    description="مكتبة للتشفير المتقدم باستخدام Caesar Cipher مع دعم الأرقام",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

