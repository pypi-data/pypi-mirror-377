from setuptools import setup


with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='cxnstr',
    version='1.1.5',
    author="Joe Boyd",
    author_email="josefuboyd@gmail.com",
    description="Parse database connection strings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jobo3208/cxnstr",
    py_modules=['cxnstr'],
    entry_points={
        'console_scripts': ['cxnstr=cxnstr:main'],
    },
    install_requires=[
        'six>=1.11.0',
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Database",
    ],
)
