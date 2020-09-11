from setuptools import setup, find_packages

import os

path = os.path.abspath(os.path.dirname(__file__))


def read(filename):
    with open(os.path.join(path, filename), encoding="utf-8") as f:
        return f.read()


setup(
    name="emissionsapi-worldmap-creator",
    version="0.2",
    description="Emissions API's World Map image creator",
    author="Emissions API Developers",
    license="MIT",
    url="https://github.com/emissions-api/emissionsapi-worldmap-creator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Framework :: Matplotlib",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    install_requires=[
        "geopandas",
        "h3",
        "matplotlib",
        "descartes",
    ],
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    entry_points={
        "console_scripts": [
            "emissionsapi-worldmap-creator"
            " = emissionsapi_worldmap_creator.__main__:main"
        ]
    },
)
