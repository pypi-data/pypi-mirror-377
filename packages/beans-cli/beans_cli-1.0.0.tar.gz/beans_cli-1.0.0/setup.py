from setuptools import setup

setup(
    name='beans-cli',
    version='1.0.0',
    author='Arkadiusz Hypki',
    description='BEANS CLI is a package with BEANS Python scripts, and helper classes.',
    packages=['beans'],
    include_package_data=True,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
    ],
    entry_points = {
        'console_scripts': [
            'beans = beans.beans:main'
        ]
    },
)
