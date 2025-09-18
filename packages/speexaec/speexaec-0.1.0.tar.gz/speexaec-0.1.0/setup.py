from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import os
import numpy as np
from Cython.Build import cythonize

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

class CustomBuildExt(build_ext):
    def build_extensions(self):
        for ext in self.extensions:
            if self.compiler.compiler_type == 'unix':
                ext.extra_compile_args = list(set((ext.extra_compile_args or []) + ["-fPIC"]))
        super().build_extensions()

setup(
    name="speexaec",
    version="0.1.0",
    description="Python bindings for SpeexDSP audio processing library",
    packages=["speexaec"],
    package_dir={"": "src"},
    ext_modules=cythonize(extensions, language_level="3"),
    cmdclass={"build_ext": CustomBuildExt},
)
