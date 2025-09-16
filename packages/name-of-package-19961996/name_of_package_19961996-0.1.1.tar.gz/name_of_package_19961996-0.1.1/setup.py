from setuptools import setup, find_packages

setup(
    name="name_of_package_19961996",   # Tên package, phải duy nhất trên PyPI
    version="0.1.1",
    author="Chiêu Nguyễn",
    author_email="your_email@example.com",
    description="Demo package upload lên PyPI",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
)
