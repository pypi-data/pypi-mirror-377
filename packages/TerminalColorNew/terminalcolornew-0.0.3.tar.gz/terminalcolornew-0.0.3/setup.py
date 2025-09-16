from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='TerminalColorNew',
  version='0.0.3',
  author='buixobra',
  author_email='evgenijsattorovphoto@gmail.com',
  description='can change color of console output',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/ZheniaNSK/TerminalColorNew',
  packages=find_packages(),
  install_requires=['rich>=13.7.1'],
  classifiers=[],
  keywords='',
  project_urls={},
  python_requires='>=3.10'
)