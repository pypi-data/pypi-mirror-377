from setuptools import setup, find_packages

setup(
    name="simple-calculator-noura-ghanem",  # اسم الحزمة باللاتيني
    version="0.1.0",
    author="Noura Ghanem",
    author_email="your_email@example.com",
    description="A simple calculator package for basic math operations",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/simple-calculator",  # اختياري
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
