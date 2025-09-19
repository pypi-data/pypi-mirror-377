from setuptools import setup, find_packages

setup(
    name="pintor-pintor-pca",
    version="1.0.0",
    author="Pedro",
    description="Biblioteca para aplicar o método de PCA",
    url="https://github.com/PedroPintor/pintor-pintor-pca.git",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "factor-analyzer>=0.4.0"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
