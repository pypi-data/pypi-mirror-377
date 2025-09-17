from setuptools import setup, find_packages

setup(
    name="crea",
    version="0.1.5",
    packages=find_packages(),
    install_requires=[ "scipy", "scikit-learn", "numpy"],  
    include_package_data=True,
    description="A library for selecting and comparing word vectors from the CREA dataset",
    author="Alex Skitowski",
    author_email="askitowski@mcw.edu",
    url="https://github.com/askitowski1/CREA-Vectors/tree/main/crea_library",
)
 