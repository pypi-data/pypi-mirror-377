import setuptools
import os


with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()


with open(os.path.join("optic_object_wavefronts", "version.py")) as f:
    txt = f.read()
    last_line = txt.splitlines()[-1]
    version_string = last_line.split()[-1]
    version = version_string.strip("\"'")


setuptools.setup(
    name="optic_object_wavefronts",
    version=version,
    description="Representing optical components using object wavefronts",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Sebastian Achim Mueller",
    author_email="sebastian-achim.mueller@mpi-hd.mpg.de",
    url="https://github.com/cherenkov-plenoscope/optic_object_wavefronts",
    packages=[
        "optic_object_wavefronts",
        "optic_object_wavefronts.optics",
        "optic_object_wavefronts.primitives",
        "optic_object_wavefronts.geometry",
        "optic_object_wavefronts.geometry.grid",
    ],
    package_data={
        "optic_object_wavefronts": [
            os.path.join("materials", "media", "*"),
            os.path.join("materials", "surfaces", "*"),
        ],
    },
    install_requires=[
        "shapely",
        "scipy",
        "triangle_mesh_io>=0.1.3",
        "json-numpy-sebastian-achim-mueller>=0.1.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
)
