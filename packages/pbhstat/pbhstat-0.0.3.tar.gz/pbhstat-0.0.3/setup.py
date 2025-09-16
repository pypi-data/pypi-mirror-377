from distutils.core import setup
setup(
  name = 'pbhstat',
  packages = ['pbhstat'],
  version = '0.0.3',
  license='MIT',
  description = 'A Python code for calculating the primordial black hole mass function and abundance.',
  author = 'Philippa Cole and Jacopo Fumagalli',
  author_email = 'philippa.cole@unimib.it',
  url = 'https://github.com/pipcole/pbhstat',
  download_url = 'https://github.com/pipcole/pbhstat/archive/refs/tags/v.0.0.3.tar.gz',
  keywords = ['PBH', 'abundance', 'mass function'],
  install_requires=[
          'numpy',
          'scipy',
          'matplotlib',
          'tqdm',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',

    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
  ],
)
