from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='ConsoleRGBColor',
  version='0.0.1',
  author='buixobra',
  author_email='evgenijsattorov@gmail.com',
  description='can change color of console output',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='',
  packages=find_packages(),
  install_requires=['opencv-python>=4.6.0.66', 'numpy>=1.26.3', 'requests>=2.32.2', 'rich>=13.7.1'],
  classifiers=[],
  keywords='',
  project_urls={},
  python_requires='>=3.10'
)