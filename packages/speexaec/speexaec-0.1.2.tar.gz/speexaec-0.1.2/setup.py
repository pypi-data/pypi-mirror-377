from setuptools import setup, Extension
import os
import numpy as np
from Cython.Build import cythonize

# Read long description from README for PyPI
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(THIS_DIR, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

include_dirs = [
    np.get_include(),
    os.path.join(os.environ.get("SPEEXDSP_PREFIX", "/usr/local"), "include"),
]

library_dirs = [
    os.path.join(os.environ.get("SPEEXDSP_PREFIX", "/usr/local"), "lib"),
]

link_args = ["-Wl,-rpath,/usr/local/lib"]

# Build a single unified extension from the new _speexaec module (.pyx only)
extensions = [
    Extension(
        name="speexaec._speexaec",
        sources=["src/speexaec/_speexaec.pyx"],
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=["speexdsp"],
        extra_compile_args=["-O3", "-fPIC"],
        extra_link_args=link_args,
    )
]

setup(
    name="speexaec",
    version="0.1.2",
    description="Python bindings for SpeexDSP audio processing library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="J.David Luque",
    author_email="jdluque@leitat.org",
    url="https://github.com/leitat-raise/package-speexaec",
    project_urls={
        "Source": "https://github.com/leitat-raise/package-speexaec",
        "Tracker": "https://github.com/leitat-raise/package-speexaec/issues",
    },
    license="BSD-3-Clause",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Cython",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=["numpy>=2"],
    packages=["speexaec"],
    package_dir={"": "src"},
    package_data={"speexaec": ["py.typed", "*.pyi"]},
    include_package_data=True,
    ext_modules=cythonize(extensions, language_level="3"),
)
