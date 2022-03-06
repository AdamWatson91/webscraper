from setuptools import setup
from setuptools import find_packages

setup(
    name='Webscraper',
    version='0.0.1',
    description='Webscraper that allows you to extract data from websites',
    url='https://github.com/AdamWatson91/webscraper.git',
    author='Adam Watson',  # Your name
    license='MIT',
    packages=find_packages(),
    install_requires=['selenium', 'webdriver_manager'],
)
