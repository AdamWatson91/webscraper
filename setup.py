from setuptools import setup
from setuptools import find_packages

setup(
    name='Webscraper', ## This will be the name your package will be published with
    version='0.0.1', 
    description='Webscraper that allows you to extract data from websites',
    url='https://github.com/AdamWatson91/webscraper.git', # Add the URL of your github repo if published 
                                                                   # in GitHub
    author='Adam Watson', # Your name
    license='MIT',
    packages=find_packages(), # This one is important to explain. See the notebook for a detailed explanation
    install_requires=['selenium', 'webdriver_manager'], # For this project we are using two external libraries
                                                     # Make sure to include all external libraries in this argument
)