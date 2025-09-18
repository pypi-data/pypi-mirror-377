from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="easyscript",
    version="0.2.0",
    author="EasyScript",
    author_email="java4life@gmail.com",
    description="A simple scripting language that blends Python and JavaScript syntax",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rhulha/easyscript",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/rhulha/easyscript/issues",
        "Source": "https://github.com/rhulha/easyscript",
        "Documentation": "https://github.com/rhulha/easyscript#readme",
    },
)