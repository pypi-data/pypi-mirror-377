
from setuptools import setup, find_packages

setup(
    name="simple_advancedcipherlib",  
    version="1.0.1",
    author="Naser Hnysh",
    author_email="naserhnysh@gmail.com",
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

