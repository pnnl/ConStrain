from setuptools import setup, find_packages
from pathlib import Path

# read the contents of the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
    name="constrain",
    version="0.3.1",
    description="ConStrain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "data",
        "simulation",
        "verification",
        "building",
        "bms",
        "hvac",
        "commissioning",
    ],
    url="https://github.com/pnnl/ConStrain",
    author="Pacific Northwest National Laboratory",
    author_email="yan.chen@pnnl.gov",
    packages=find_packages(),
    install_requires=[
        "brickschema",
        "numpy",
        "matplotlib",
        "pandas",
        "seaborn",
        "scipy",
        "eppy",
        "fuzzywuzzy",
        "tqdm",
        "scikit-learn",
        "uuid",
        "pydash",
        "PyYAML",
    ],
)
