import setuptools

setuptools.setup(
    entry_points={
        'console_scripts': [
            'opp-db = opp.tools.dbmgr:main',
        ],
    }
)
