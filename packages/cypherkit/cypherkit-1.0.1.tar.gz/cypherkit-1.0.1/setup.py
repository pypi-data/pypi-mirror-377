from setuptools import setup, find_packages

setup(
    name='cypherkit',
    version='1.0.1',
    packages=find_packages(),
    install_requires=[
        'pycryptodome',
        'Pillow',
    ],
    author='Fahim Ahmed',
    author_email='fahimdidnt@gmail.com',
    description='A basic library for cryptographic operations like hashing, encryption, and steganography',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/fahimdidnt/cypherkit',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
