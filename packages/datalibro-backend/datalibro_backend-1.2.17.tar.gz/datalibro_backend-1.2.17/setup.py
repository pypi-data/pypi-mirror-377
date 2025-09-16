import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="datalibro_backend",
  version="1.2.17",
  author="lucy",
  author_email="lucy@petlibro.com",
  description="A small package for your backend service",
  long_description=long_description,
  long_description_content_type="text/markdown",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
  install_requires=[
    "pymysql",
    "pandas",
    "pyspark==3.5.0",
    "pyyaml"
  ],
  extras_require={
    "openmetadata": [
      "pyspark==3.5.0"
    ]
  },
)

