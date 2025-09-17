#! /usr/bin/env python

from setuptools import setup, find_packages

vers = "0.0.7.6"

setup(
    name="veilcord-tls",
    version=vers,
    description="VeilCord // @imvast",
    long_description_content_type="text/markdown",
    long_description=open("README.md", encoding="utf-8").read(),
    packages=[
        "veilcord_tls",
        "veilcord_tls.models",
    ],  # find_packages(exclude=["tests"], include=["types"]),
    author="@imvast",
    url=f"http://pypi.python.org/pypi/veilcord",
    author_email="dev@vast.sh",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    project_urls={
        "Homepage": "https://github.com/imvast",
        "Suggestions": "https://github.com/imvast/veilcord/issues",
        "Support": "https://t.me/skiddos",
    },
    python_requires="~=3.8",
    install_requires=[
        "terminut>=0.0.0.901",
        "colorama>=0.4.6",
        "requests>=2.30.0",
        "httpx>=0.25.0",
        "tls_client>=0.2.1",
        "websocket-client>=1.5.1",
        "google-re2>=1.1",
    ],
)
