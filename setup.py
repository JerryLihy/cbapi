from setuptools import setup, find_packages

setup(
    name = "cbapi",
    version = "1.0.0",
    url = "https://github.com/JerryLihy/cbapi",
    author = "Hanyi Li",
    packages = find_packages(),
    install_requires = ["requests==2.18.4", "numpy==1.16.4", "pandas==0.25.3", "multiprocess==0.70.9"],
    description = "A full-featured API (application programming interface) library to allow downloading and presenting organization and people data from Crunchbase.",
)

