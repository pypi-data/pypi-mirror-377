from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="zebubot",
    version="0.0.1b2",
    author="Zebu Team",
    author_email="it@zebuetrade.com",
    description="A high-performance algorithmic trading platform for Indian stock markets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/zebubot/zebubot",
    # project_urls={
    #     "Bug Reports": "https://github.com/zebubot/zebubot/issues",
    #     "Source": "https://github.com/zebubot/zebubot",
    #     "Documentation": "https://github.com/zebubot/zebubot#readme",
    # },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
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
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.9',
            'mypy>=0.910',
        ],
        'full': [
            'click>=8.0.0',
            'python-dotenv>=0.19.0',
            'numpy>=1.21.0',
            'websockets>=10.0',
            'asyncio-mqtt>=0.11.0',
            'cython>=0.29.0',
        ],
    },
    entry_points={
        "console_scripts": [
            "zebubot=zebubot.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "zebubot": ["config/*.yaml", "config/*.json", "templates/*.py"],
    },
    keywords="trading, api, algorithmic-trading, stock-market, noren, myntapi, india, zebubot",
    zip_safe=False,
)
