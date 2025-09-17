from setuptools import setup, find_packages

setup(
    name="pyrssi",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "pyobjc; platform_system=='Darwin'"
    ],
    python_requires=">=3.7",
    description="Get Wi-Fi RSSI on Mac, Windows, or Linux",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ericdennis7/pyrssi",
    author="Eric Dennis",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
)
