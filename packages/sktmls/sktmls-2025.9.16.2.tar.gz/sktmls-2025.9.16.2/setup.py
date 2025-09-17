import setuptools


def load_long_description():
    with open("README.md", "r") as f:
        long_description = f.read()
    return long_description


def get_version():
    with open("sktmls/__init__.py", "r") as f:
        for line in f.readlines():
            if line.startswith("__version__"):
                return line.split('"')[1]
        else:
            raise TypeError("NO SKTMLS_VERSION")


setuptools.setup(
    name="sktmls",
    version=get_version(),
    author="SKTMLS",
    author_email="mls@sktai.io",
    description="MLS SDK",
    long_description=load_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/sktaiflow/mls-sdk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "aiohttp[speedups]",
        "autogluon.tabular==1.4.0",
        "boto3",
        "catboost==1.2.8",
        "haversine==2.9.0",
        "joblib",
        "lightgbm==4.6.0",
        "numpy==2.3.3",
        "pandas==2.3.2",
        "pytz",
        "requests",
        "scikit-learn==1.7.2",
        "simplejson",
        "torch==2.8.0",
        "xgboost==3.0.5",
        "ipyparallel==9.0.1",
        "hvac==2.3.0",
        "distributed==2025.9.0",
        "dask==2025.9.0",
    ],
)
