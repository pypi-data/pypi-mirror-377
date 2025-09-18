from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='python-nicepay',
    version='1.1.0',
    packages=find_packages(),
    include_package_data=True,
    description='This is the Official Python API client / library for NICEPAY Payment API',
    long_description_content_type='text/markdown',
    long_description=long_description,
    author='Harfa Thandila',
    author_email='harfa.thandila@nicepay.co.id',
    url='https://github.com/nicepay-dev/python-nicepay',
    license='',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'pycryptodome==3.21.0',
        'requests==2.32.3'
    ],
    keywords=["pypi", "config", "nicepay"],
    project_urls={
        "Documentation": "https://github.com/nicepay-dev/python-nicepay/blob/main/README.md",
        "Source": "https://github.com/nicepay-dev/python-nicepay",
    },

)
