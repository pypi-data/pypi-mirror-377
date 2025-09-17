from setuptools import setup, find_packages

setup(
    name="AgLight",
    version="0.1.0",
    description="Ultra-accelerating decorator for scientific and numerical Python functions.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="AG",
    packages=find_packages(),
    install_requires=[
        "numpy"
    ],
    extras_require={
        "numba": ["numba"]
    },
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_data={"": ["README.md"]},
)
