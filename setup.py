from setuptools import setup, find_packages
from semantic_version import Version


"""
To relase package update `package_version` and commit/push changes, then run
$ python setup.py sdist bdist_wheel
$ twine upload dist/*

for twine upload to work, must have credentials in .pypirc file
"""

with open('README.md', 'r') as fh:
    long_description = fh.read()

package_version = Version(major=0, minor=7, patch=4, prerelease=('alpha', '2'))
# package_version = Version('0.5.0')  # Use this when installing locally with pip install -e

setup(
    name='xd_cwl_utils',
    version=str(package_version),
    packages=find_packages(),
    url='https://github.com/xDBio-Inc/xd-cwl-utils',
    license='Apache 2.0',
    author='Karl Sebby',
    author_email='karl.sebby@xdbio.com',
    description='Tool for managing CWL file repositories.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires = [
        'setuptools',
        'requests',
        'ruamel.yaml >= 0.15, <=0.16',
        'semantic-version',
        'pandoc-include',
        'cwltool',
    ],
    entry_points={
        'console_scripts': ["xd-cwl-validate=xd_cwl_utils.validate_metadata:main", "xd-cwl-add=xd_cwl_utils.add_content:main"]
                  },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires=">=3",
)
