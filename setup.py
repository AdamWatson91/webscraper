from setuptools import setup
from setuptools import find_packages

setup(
    name='recipe_webscraper',
    version='0.0.1',
    description='A webscraper that allows you to navigate and extract data from websites',
    url='https://github.com/AdamWatson91/webscraper.git',
    author='Adam Watson',  # Your name
    license='MIT',
    packages=find_packages(),
    install_requires=['selenium', 'webdriver_manager'],
)
