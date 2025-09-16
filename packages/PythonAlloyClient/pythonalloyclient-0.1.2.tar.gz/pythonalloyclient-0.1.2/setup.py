from setuptools import setup, find_packages

setup(
    name='PythonAlloyClient',
    version='0.1.2',
    author='Mrigank Pawagi',
    author_email='mrigankpawagi@gmail.com',
    description='Python Client for the Alloy Language Server',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/mrigankpawagi/PythonAlloyClient',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.6',
    install_requires=[
        dep.strip() for dep in open('requirements.txt').readlines()
    ],
    package_data={'PythonAlloyClient': ['resources/*']}
)
