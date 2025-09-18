from distutils.core import setup
from setuptools import find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(name='iOSMonitor',
      version='1.0.4',
      description='iOS Monitor',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='cfr',
      author_email='1354592998@qq.com',
      install_requires=[
          'pymobiledevice3>=4.26.2',
      ],
      license='MIT',
      packages=find_packages(),
      platforms=['all'],
      classifiers=[],
      python_requires='>=3.10.0',

      entry_points={
          'console_scripts': ['iOSMonitor=monitor:run']  # 修改为新的入口点
      },

      )