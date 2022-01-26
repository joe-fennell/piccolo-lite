import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="piccololite",  # Replace with your own username
    version="0.0.1",
    author="Joseph T. Fennell",
    author_email="info@joefennell.org",
    description="Lightweight Piccolo system i/o and calibration module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joe-fennell/piccolo-lite",
    include_package_data=True,
    packages=setuptools.find_packages(),
    install_requires=[
        'xarray',
        'numpy',
        'json',
        'pandas',
        'netcdf4'
    ],
    scripts=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
