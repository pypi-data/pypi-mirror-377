from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "A flexible data pipeline library for custom data processing workflows"

setup(
    name="pipelinehub",
    version="0.1.0",
    author="Rahul Paul",
    author_email="paul.rahulxj100@gmail.com",
    description="A flexible data pipeline library for custom data processing workflows",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/rahulxj100/pipelinehub",
    project_urls={
        "Bug Reports": "https://github.com/rahulxj100/pipelinehub/issues",
        "Source": "https://github.com/rahulxj100/pipelinehub",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords=["pipeline", "data", "processing", "workflow", "etl"],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": ["pytest>=6.0", "black", "flake8", "mypy"],
    },
    include_package_data=True,
    zip_safe=False,
)