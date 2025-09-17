from setuptools import setup, find_packages

setup(
    name="aggarage",
    version="0.4.5",
    author="AG",
    description="An open-source python package with multiple python tools.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "numba>=0.57.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "pyarrow>=10.0.0",
    ]
)
