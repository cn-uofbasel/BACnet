import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="subjectivechat-pkg",
    version="1",
    description="A package for access to the sqLite database for the BACnet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cn-uofbasel/BACnet/tree/master/groups/03-subChat/UI",
    packages=setuptools.find_packages(),
    install_requires=[
          'pickle',
          'pyglet',
          'PIL',
          'base64',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
    python_requires='>=3.6',
)
