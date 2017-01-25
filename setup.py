from setuptools import setup, find_packages

setup(
    name='opp',
    version='1.0.0',
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'opp-db=opp.tools.dbmgr:main',
        ],
    },
)
