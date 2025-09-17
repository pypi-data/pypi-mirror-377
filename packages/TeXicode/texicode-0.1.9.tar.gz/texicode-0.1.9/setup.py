from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='TeXicode',
    version='0.1.9',
    py_modules=[
        'main',
        'lexer',
        'arts',
        'parser',
        'node_data',
        'symbols_art',
        'renderer',
        'pipeline',
    ],
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'txc=main:main',
        ],
    },
    install_requires=[
        # List your dependencies here
    ],
    long_description=description,
    long_description_content_type="text/markdown",
)
