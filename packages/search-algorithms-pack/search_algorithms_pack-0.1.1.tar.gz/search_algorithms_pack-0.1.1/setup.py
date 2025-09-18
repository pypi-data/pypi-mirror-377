from setuptools import setup ,find_packages
import pathlib
long_description = pathlib.Path("README.md").read_text()
setup(
  name = 'search-algorithms-pack',
  version='0.1.1',
  packages=find_packages(),
  description='Consists of searching algorithms(Linear,Binary and Jump)',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author="ARpit Kumar",
  author_email="arpitkumar172004@gmail.com",
  license="MIT"
)