from setuptools import setup, find_packages

setup(
    name='smev_int',
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-mock'],
)
