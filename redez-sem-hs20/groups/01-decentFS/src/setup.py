import setuptools

setuptools.setup(
    name="decentFS",
    version="0.0.0-dev",
    description="A decentral filesystem, inspired by hyperdrive",
    url="https://github.com/cn-uofbasel/BACnet",
    packages=setuptools.find_packages(),
    install_requires=[
          'cbor2',
          'pynacl',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
