from setuptools import setup, find_packages

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="topsisx",
    version="0.1.3",
    author="Suvit Kumar",
    author_email="suvitkumar03@gmail.com",
    description="A Python library for Multi-Criteria Decision Making (TOPSIS, AHP, VIKOR, Entropy, etc.)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SuvitKumar003/ranklib",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "fpdf",
        "matplotlib",
        "streamlit",
        "fastapi",
        "uvicorn",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "topsisx = topsisx.cli:main",  # CLI command for global use
        ],
    },
)
