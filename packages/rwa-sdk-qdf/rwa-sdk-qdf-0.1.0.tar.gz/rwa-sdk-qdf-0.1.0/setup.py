"""
Setup configuration for RWA.xyz Python SDK
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="rwa-sdk-qdf",  # QuantDeFi RWA SDK
    version="0.1.0",
    author="samthedataman",
    author_email="",  # Add your email if desired
    description="QuantDeFi.ai RWA SDK - Professional toolkit for tokenized asset data analysis | $297B+ tracked assets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://quantdefi.ai",
    project_urls={
        "Website": "https://quantdefi.ai",
        "Bug Tracker": "https://github.com/quantdefi/rwa-sdk-qdf/issues",
        "Documentation": "https://github.com/quantdefi/rwa-sdk-qdf#readme",
        "Source Code": "https://github.com/quantdefi/rwa-sdk-qdf",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
            "twine>=4.0.0",
            "wheel>=0.38.0",
            "build>=0.10.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    keywords="rwa blockchain tokenization stablecoins treasuries api sdk defi crypto web3 real-world-assets",
)