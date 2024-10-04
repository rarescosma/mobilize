from setuptools import find_packages, setup

setup(
    name="mobilize",
    version="0.1.3",
    description="http URL to epub + mobi converter",
    entry_points={
        "console_scripts": ["mobilize=mobilize.main:main"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
    license="UNLICENSE",
    keywords="epub, mobi, kindle, readability, bs4",
    packages=find_packages(exclude=["docs", "tests*"]),
    include_package_data=True,
)
