from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="Glassdoorscrape",
    version="0.0.1",
    description="In this we are scraping the FAANG companies interview data",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/adityakumarpinjala/Glassdoorscraping",
    author="AdityaPinjala",
    author_email="adityakumarpinjala@gmail.com",
    keywords="package creation",
    license="MIT",
    #packages=['Glassdoorscrape'],
    install_requires=[],
    include_package_data=True,
)