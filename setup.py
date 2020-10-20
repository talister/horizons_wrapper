from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["astropy>=4.0", "astroquery"]

setup(
    name="horizons_wrapper",
    version="0.0.1",
    author="Tim Lister",
    author_email="tlister@lco.global",
    description="A package to wrap use of the astroquery JPL HORIZONS query tool",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/talister/horizons_wrapper/",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
    ],
)
