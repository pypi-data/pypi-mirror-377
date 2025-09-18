from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tsadmetrics",
    version="1.0.4",
    author="Pedro Rafael Velasco Priego",
    author_email="i12veprp@uco.es",
    description="Librería para evaluación de detección de anomalías en series temporales",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pathsko/TSADmetrics",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy==1.24.4",
        "pandas==2.0.3",
        "PATE==0.1.1",
        "PyYAML==6.0.2"
    ],
    extras_require={
        "dev": [
            "pytest==8.3.5",
            "iniconfig==2.1.0",
            "pluggy==1.5.0",
            "tomli==2.2.1",
            "exceptiongroup==1.3.0",
            "ipython>=7.0",
            "sphinx",
            "sphinx-rtd-theme",
            "numpydoc",
            "myst-parser",
        ],
    }
)
