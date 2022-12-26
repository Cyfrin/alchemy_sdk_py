from setuptools import setup
import os


here = os.path.abspath(os.path.dirname(__file__))
with open("README.md", "r", "utf-8") as f:
    readme = f.read()

about = {}
with open(os.path.join(here, "alchemy_sdk_py", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    license=about["__license__"],
    install_requires=[
        "certifi",
        "charset-normalizer",
        "idna",
        "requests",
        "urllib3",
    ],
    packages=[about["__title__"]],
    python_requires=">=3.7, <4",
    url="https://github.com/alphachainio/alchemy_sdk_py",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["alchemy_sdk_py"],
)
