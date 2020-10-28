import os
import io
import re
from setuptools import setup, find_packages


def read(*names, **kwargs):
    with io.open(os.path.join(os.path.dirname(__file__), *names),
                 encoding=kwargs.get("encoding", "utf8")) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


README = read('README.md')
VERSION = find_version('seismic_canvas', '__init__.py')

setup(
    # Metadata
    name='seismic_canvas',
    version=VERSION,
    author='Yunzhi Shi',
    author_email='yunzhi.shi.phd@gmail.com',
    url='https://github.com/yunzhishi/seismic-canvas',
    description='An interactive 3D visualization tool mainly designed for seismic data',
    long_description=README,
    long_description_content_type='text/markdown',
    license='MIT',

    # Package info
    packages=find_packages(),
    include_package_data=True,
    install_requires=['numpy', 'vispy', 'PyQt5', 'PyOpenGL', 'matplotlib'],

    zip_safe=True,

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)