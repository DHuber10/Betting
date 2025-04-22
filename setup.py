from setuptools import setup, find_packages

setup(
    name="mlb_odds",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "tabulate",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "mlb-odds=mlb_odds.main:main",
        ],
    },
    author="Your Name",
    description="MLB betting odds analyzer",
) 