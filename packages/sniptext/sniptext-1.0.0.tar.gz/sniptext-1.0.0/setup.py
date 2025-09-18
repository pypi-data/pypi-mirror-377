#!/usr/bin/env python3
"""
Setup script for SnipText - Screenshot OCR Tool
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "SnipText"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="sniptext",
    version="1.0.0",
    author="Aaditya Kanjolia",
    author_email="a21kanjolia@gmail.com",
    description="A desktop screenshot OCR tool that automatically copies extracted text to clipboard",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/aadityakanjolia4",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'sniptext=sniptext.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="screenshot ocr clipboard text-extraction desktop-tool",
    project_urls={
    },
)
