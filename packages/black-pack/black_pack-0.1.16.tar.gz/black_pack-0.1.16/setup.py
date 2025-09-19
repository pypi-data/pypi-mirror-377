import setuptools
import os

with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()


with open(os.path.join("black_pack", "version.py")) as f:
    txt = f.read()
    last_line = txt.splitlines()[-1]
    version_string = last_line.split()[-1]
    version = version_string.strip("\"'")


setuptools.setup(
    name="black_pack",
    version=version,
    description=("Linting and structural checking for python-packages"),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/cherenkov-plenoscope/black_pack",
    author="Sebastian Achim Mueller",
    author_email="sebastian-achim.mueller@mpi-hd.mpg.de",
    packages=["black_pack", "black_pack.apps"],
    package_data={"black_pack": [os.path.join("resources", "*")]},
    install_requires=[
        "black",
        "cython-lint",
        "toml",
        "yamlcore",
        "restructuredtext-lint",
        "pyyaml",
        "dictdiffer",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    entry_points={
        "console_scripts": [
            "black-pack=black_pack.apps.main:main",
        ]
    },
)
