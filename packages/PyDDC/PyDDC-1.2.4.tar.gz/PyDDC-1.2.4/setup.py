from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_desc = fh.read()

setup(
    name="PyDDC",
    version='1.2.4',
    author="Sayan Sen, Scott K. Hansen",
    package=find_packages(),
    install_requires=[
        'python>=3.11.0',
        'CO2Br==0.0.1',
        'numpy>=1.26.4',
        'scipy>=1.15.2',
        'matplotlib>=3.6.2',
        'gstools>=1.4.1', 
        'numba>=0.60.0', 
        'tables>=3.10.2',
        'tqdm>=4.66.2',
        'h5py>=3.7.0' 
    ],
    description="Simulates density-driven convection of single phase CO2--brine mixture",
    long_description=long_desc,
    long_description_content_type="text/markdown"
)
