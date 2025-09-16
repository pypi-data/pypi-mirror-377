from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="CustomPyQt6",
    version="0.1.0",
    author="MineMish",
    author_email="your.email@example.com",
    description="Упрощенная библиотека для создания красивых приложений на PyQt6",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your_username/CustomPyQt6",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "PyQt6>=6.0.0",
    ],
)