"""Legacy setuptools entry point; the canonical metadata lives in pyproject.toml."""

from setuptools import setup

setup(name='uscis-case-status',
      version='1.0.1',
      description='USCIS Status Checker',
      url='https://github.com/pkhanpara/uscis-case-status',
      author='Poojan Khanpara',
      author_email='poojankhanpara@gmail.com',
      license='MIT',
      packages=['uscis_case_status'],
       install_requires=[
          'selenium',
          'undetected-chromedriver',
          # undetected_chromedriver imports distutils, removed in Python 3.12
          'setuptools'
      ],
      entry_points={
          'console_scripts': [
              'uscis-case-status=uscis_case_status.__main__:main',
          ],
      },
      zip_safe=False)
