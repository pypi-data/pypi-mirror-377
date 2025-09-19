import os
import sys

from setuptools import setup, find_packages
from distutils.command.build_py import build_py


classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
Programming Language :: Python :: 3.13
Topic :: Software Development :: Compilers
Operating System :: Unix
"""

requirements = ["ply>=3.11"]
(major,) = sys.version_info[:1]  # Python version
if major < 3:
    raise ImportError("This package requires Python 3")


def read(*rel_names):
    return open(os.path.join(os.path.dirname(__file__), *rel_names)).read()


setup(
    name="slimit3k",
    version="0.9.0",
    url="https://slimit.readthedocs.io",
    cmdclass={"build_py": build_py},
    license="MIT",
    description="SlimIt - JavaScript minifier",
    author="Ruslan Spivak",
    author_email="ruslan.spivak@gmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=requirements,
    zip_safe=False,
    entry_points="""\
    [console_scripts]
    slimit = slimit.minifier:main
    """,
    classifiers=filter(None, classifiers.split("\n")),
    long_description=read("README.rst") + "\n\n" + read("CHANGES"),
    extras_require={"test": []},
)
