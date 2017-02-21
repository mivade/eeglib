from setuptools import find_packages, setup

long_description = "Tools for processing EEG data files."

setup(
    name="eeglib",
    version="0.1.dev",
    author="Michael V. DePalatis",
    author_email="depalati@sas.upenn.edu",
    description="Tools for processing EEG data",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "tables"
    ],
    extras_require={
        "full": [
            "tqdm"
        ]
    }
)
