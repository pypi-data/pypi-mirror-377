from setuptools import setup,find_packages

with open('README.md', 'r') as f:
    description = f.read()
setup(name="adcpasciireader",
      version="1.1.3",
      description="Code for reading and plotting adcp data from classic ascii output",
      long_description=description,
      author="AP",
      packages=["adcpasciireader"],
      install_requires = [],
      )