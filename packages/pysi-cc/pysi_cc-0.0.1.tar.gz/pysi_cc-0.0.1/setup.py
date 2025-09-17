from setuptools import setup, find_packages

setup(
    name='pysi_cc',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'torch',
        'numpy'
    ],
    author='Federico J. Gonzalez',
    description='Library to train and use NN models for physical systems',
    python_requires='>=3.7',
)

