from setuptools import setup, find_packages

setup(
    name='token_sub_info',
    version='0.1.17',
    packages=find_packages(),
    install_requires=[
        'cryptography==40.0.0',
        'fastapi==0.104.1',
        'PyJWT==2.8.0'
    ],
    author='Ilya Mikhasik',
    author_email='imikhassik@gmail.com',
    description='A library for extracting information from jwt tokens.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)
