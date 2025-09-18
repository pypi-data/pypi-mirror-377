from setuptools import setup, find_packages

setup(
    name="tracker_utils_tl",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "boto3"
    ],
    python_requires=">=3.8",
)

"""
Update the version number in setup.py or pyproject.toml. Example:

version="0.1.1"  # increment from 0.1.0


Rebuild the package:

python setup.py sdist bdist_wheel


Upload the new version to PyPI:

twine upload dist/*


Install the new version in your nodes:

pip install --upgrade tracker-utils-tl
"""