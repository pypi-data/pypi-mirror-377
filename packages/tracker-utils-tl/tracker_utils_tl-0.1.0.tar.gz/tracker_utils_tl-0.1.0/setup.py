from setuptools import setup, find_packages

setup(
    name="tracker_utils_tl",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3"
    ],
    python_requires=">=3.8",
)
