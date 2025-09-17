from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="blazegraph-io",
    version="0.0.1",
    author="Amplify Technology",
    description="Document intelligence platform - coming soon",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://blazegraph.io",
    project_urls={
        "Homepage": "https://blazegraph.io",
        "Documentation": "https://blazegraph.io/docs",
        "Source": "https://github.com/amplifytechnology/blazegraph-io",
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Markup",
    ],
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[],
    keywords="document intelligence graph pdf analysis parsing parser",
)
