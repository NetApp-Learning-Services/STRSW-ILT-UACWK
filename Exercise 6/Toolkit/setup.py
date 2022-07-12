import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="netapp-astra-toolkits",
    version="2.0",
    scripts=["toolkit.py"],
    py_modules=["astraSDK"],
    data_files=[("config", ["config.yaml"])],
    author="Josh Paetzel",
    author_email="Josh.Paetzel@netapp.com",
    description="Toolkit and SDK for interacting with Astra",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NetApp/netapp-astra-toolkits",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
