from setuptools import setup, find_packages

setup(name='sodapclient',
      version='0.3.0',
      description='A simple OpenDAP client library',
      author='Marcus Donnelly',
      author_email='marcus.k.donnelly@gmail.com',
      url='https://github.com/marcuskd/sodapclient',
      license='BSD 3-Clause',
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3',
                   'Topic :: Scientific/Engineering'
                   ],
      keywords=['OpenDAP',
                'Environment',
                'Science'
                ],
      packages=find_packages(),
      install_requires=['numpy >= 1.23'],
      include_package_data=True
      )
