from setuptools import setup, find_packages
import os

version = '0.6.dev0'
shortdesc = ""
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(name='metachao',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development',
          ],
      keywords='',
      author='Florian Friesdorf',
      author_email='flo@chaoflow.net',
      url='http://github.com/chaoflow/metachao',
      license='BSD license',
      namespace_packages=['metachao'],
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          ],
      extras_require={
          'test': [
              'nose',
              'coverage',
              'zope.interface',
              ],
          },
      )
