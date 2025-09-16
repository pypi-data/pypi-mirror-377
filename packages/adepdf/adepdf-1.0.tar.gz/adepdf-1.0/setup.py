import setuptools
from pathlib import Path

setuptools.setup(
    name="adepdf",                      # unique name for our package, that will not collide with other packages on PyPi repository;
    version=1.0,                        # version of our package;
    long_description=Path(              # assign a string explicitly ("my description..."), or read the README.md file as a string and assign it here;
        "README.md").read_text(), 
    packages=setuptools.find_packages(  # list packages that are going to be distributed - the find method will look at our project and automatically discover
                                        # the packages that we defined (in our case "adepdf"), and return a list of those packages;
        exclude=["test", "data"])       # exclude "test" and data "directories", because they don't include any source code;
)

