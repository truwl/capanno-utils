from setuptools import setup, find_packages

"""
To release package update `package_version` and commit/push changes, then run
$ python setup.py sdist bdist_wheel
$ twine upload dist/*

for twine upload to work, must have credentials in .pypirc file
"""

with open('README.md', 'r') as fh:
    long_description = fh.read()


package_version = '0.9.6a'

setup(
    name='capanno_utils',
    version=str(package_version),
    packages=find_packages(),
    url='https://github.com/truwl/capanno-utils',
    license='Apache 2.0',
    author='Karl Sebby',
    author_email='karl.sebby@truwl.com',
    description='Tool for managing bioinformatics content repositories.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'setuptools',
        'requests',
        'ruamel.yaml >= 0.15, <=0.16',
        'semantic-version',
        'pandoc-include',
        'cwltool',
        'miniwdl'
    ],
    entry_points={
        'console_scripts': ["capanno-validate=capanno_utils.validate_content:main",
                            "capanno-add=capanno_utils.add_content:main",
                            "capanno-map=capanno_utils.make_content_maps:main",
                            "capanno-id=capanno_utils.make_ids:main",
                            "capanno-status=capanno_utils.change_status:main"]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires=">=3.6",
)
