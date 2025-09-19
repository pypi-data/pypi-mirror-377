from setuptools import setup, find_packages

setup(
    name="aasman",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # liệt kê các thư viện phụ thuộc, ví dụ "numpy>=1.25"
    ],
    author="LuuLacDinh",
    description="Một thư viện Python thú vị",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LuuLacDinh/Aasman",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)