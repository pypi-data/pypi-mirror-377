from setuptools import setup, find_packages

setup(
    name="scmlab367104703",               # Must be unique on PyPI!
    version="0.1.0",                # Follow semantic versioning
    description="Basic number theory tools: GCD calculation, solving linear Diophantine equations, and listing primes..",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="N. Amarittabut",
    author_email="nabeel65010@email.com",
    url="https://github.com/Amarit1008/ammaritproj",  # optional
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
)