import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="datarecipe",
  version="2.1.1",
  author="Hanfan Chen",
  author_email="HanfanC@outlook.com",
  description="A recipe for every data baker",
  long_description=long_description,
  long_description_content_type='text/markdown',
  url="https://github.com/Adward-Chen/databaker/tree/main",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3.10",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)