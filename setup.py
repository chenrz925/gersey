from setuptools import setup, find_packages

setup(
    name='geyser',
    version='0.10.0',
    packages=find_packages(
        where='src',
        include=['geyser*']
    ),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'geyser = geyser.__main__:main',
        ]
    },
    install_requires=[
        'importlib-metadata',
        'prompt_toolkit>=3.0.29',
        'jedi>=0.18.1',
        'Pygments>=2.12.0'
    ],
)
