from setuptools import setup, find_packages

setup(
    name="cbases",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    author="Votre Nom",
    author_email="votre@email.com",
    description="Number base conversion library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/votrenom/cbases",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)