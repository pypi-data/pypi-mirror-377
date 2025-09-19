from setuptools import setup, find_packages

setup(
    name='TAELCORE',  
    version='1.3.1',
    description="TAELCORE 3 (Topological AutoEncoder with Best Linear Combination for Optimal Reduction of Dimension) is a novel dimensionality reduction technique designed specifically for high-dimensional datasets. By combining topological autoencoding with an optimized linear combination approach, TAELCORE 3 achieves efficient, accurate, and structure-preserving reduction, making it especially suitable for complex, large-scale databases.",
    url="https://github.com/MorillaLab/Taelcore",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "giotto-tda>=0.6.0",
        "torch>=1.12.0"

    ],
    author='Ian MORILLA',  
    author_email='ian.morilla@math.univ-paris13.fr',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # License type
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',

)