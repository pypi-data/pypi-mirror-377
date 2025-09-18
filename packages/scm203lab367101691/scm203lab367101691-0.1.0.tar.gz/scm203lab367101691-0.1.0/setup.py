from setuptools import setup, find_packages

setup(
    name="scm203lab367101691",               # Must be unique on PyPI!
    version="0.1.0",                # Follow semantic versioning
    description="Find the greatest common divisor and find integers x,y such that ax + by = gcd(a,b).",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Khing",
    author_email="anchitha2005@gmail.com",
    url="https://github.com/yourusername/scm203lab367101691",  # optional
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
)