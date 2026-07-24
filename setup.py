from setuptools import setup

setup(name='uscisstatus',
      version='0.1.1',
      description='USCIS Status Checker',
      url='https://github.com/pkhanpara/uscisstatus',
      author='Poojan Khanpara',
      author_email='poojankhanpara@gmail.com',
      license='MIT',
      packages=['uscisstatus'],
       install_requires=[
          'selenium',
          'undetected-chromedriver'
      ],
      entry_points={
          'console_scripts': [
              'uscisstatus=uscisstatus.__main__:main',
          ],
      },
      zip_safe=False)
