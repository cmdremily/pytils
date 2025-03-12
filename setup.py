from setuptools import setup, find_packages

setup(
    name="pytils",
    version="0.1.0",
    description="A personal utility functions library",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.11",
    include_package_data=True,
    package_data={"pytils": ["py.typed"]},
)
