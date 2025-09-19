from setuptools import setup, find_packages

setup(
    name='ModulePyConText',
    version='0.0.1',
    author="Baibhav Kumar Jha",
    author_email="baibhavkumarjha1@gmail.com",
    description="A windows-only python package for displaying text in the console with format and give console cursor control.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Beta-Verse-Hub/PyConText",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.7",
)
