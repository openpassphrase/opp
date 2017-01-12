from setuptools import setup, find_packages

setup(
    name='OpenPassPhrase',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'opp-db=opp.tools.dbmgr:main',
        ],
    },
)
