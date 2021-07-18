#INSTALL ALL DEPENDENCIES WITH python setup.py install

from setuptools import setup
import os
thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()
setup(name="IASFrontend", install_requires=install_requires)

