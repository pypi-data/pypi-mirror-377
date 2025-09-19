from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy as np

# Extensions for Cython compilation
extensions = [
    Extension(
        "adaptive_formula.core",
        ["adaptive_formula/core.pyx"],
        include_dirs=[np.get_include()],
        language="c++",
        compiler_directives={'language_level': "3"}
    )
]

# Read README for long description
try:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Adaptive Formula SDK - Cognitive Programming Infrastructure"

setup(
    name="adaptive-formula",
    version="0.3.0",  # Synchronized version
    author="Jaime Alexander Jimenez Lozano",
    author_email="jaimeajl@hotmail.com",
    description="Cognitive Programming SDK - Eliminate conditionals with adaptive formulas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/adaptive-formula",
    packages=find_packages(),
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}),
    install_requires=[
        "numpy>=1.20.0",
        "requests>=2.25.0",
        "cython>=0.29.0",
    ],
    extras_require={
        "dev": ["pytest", "black", "mypy", "twine", "wheel"],
        "test": ["pytest", "pytest-cov"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",  # Updated from Alpha
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    zip_safe=False,
    include_package_data=True,
    package_data={
        'adaptive_formula': ['*.pyx', '*.pxd'],
    },
    # Entry points for CLI if needed in future
    entry_points={
        'console_scripts': [
            # 'adaptive-formula=adaptive_formula.cli:main',
        ],
    },
)