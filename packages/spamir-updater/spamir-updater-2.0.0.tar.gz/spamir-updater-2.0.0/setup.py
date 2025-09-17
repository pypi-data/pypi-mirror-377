from setuptools import setup, find_packages
import os

# Define requirements directly in setup.py for better packaging
requirements = [
    "requests>=2.28.0",
    "cryptography>=38.0.0",
    "packaging>=21.0",
    "psutil>=5.8.0",  # For network interface detection
    "importlib-metadata>=1.0;python_version<'3.8'",  # Backport for Python 3.7
]

# Read long description
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="spamir-updater",
    version="2.0.0",
    author="Spamir",
    author_email="spamirorg@proton.me",
    description="Secure automatic update client for Python applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spamir/spamir-updater",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
)