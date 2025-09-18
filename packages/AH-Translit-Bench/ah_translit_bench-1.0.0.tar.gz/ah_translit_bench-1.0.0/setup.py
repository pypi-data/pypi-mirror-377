# File: setup.py
from setuptools import setup, find_packages

setup(
    name='AH-Translit_Bench',
    version='1.0.0',
    author='Vilal Ali, Mohd Hozaifa Khan',
    author_email='vilal.ali@research.iiit.ac.in, mohd.hozaifa@research.iiit.ac.in',
    description='A benchmark dataset for Arabic to Hindi transliteration.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vilalali/AH-Translit-Bench', # **Ensure this is your correct GitHub URL!**
    packages=find_packages(),
    package_data={
        'AH_Translit_Bench': ['data/*.csv'], # Include CSV files in the 'data' directory
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License', # For the code
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Operating System :: OS Independent',
    ],
    keywords='arabic hindi transliteration dataset benchmark nlp msa modern standard arabic',
    python_requires='>=3.7',
    install_requires=[
        'pandas>=1.0.0',
    ],
)