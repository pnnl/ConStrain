from setuptools import setup, find_packages
from pathlib import Path

# read the contents of the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
    name="constrain",
    version="0.1.0",
    description="ConStrain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="verification",
    url="https://github.com/pnnl/ANIMATE",
    author="PNNL",
    author_email="PNNL@pnnl.gov",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "pandas",
        "seaborn",
        "scipy",
        "eppy",
        "fuzzywuzzy",
        "tqdm",
        "scikit-learn",
    ],
)
