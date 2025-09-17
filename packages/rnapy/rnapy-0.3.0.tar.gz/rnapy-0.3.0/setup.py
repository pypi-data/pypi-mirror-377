import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setuptools.setup(
    name="rnapy",
    version="0.3.0",
    author="Linorman",
    author_email="zyh52616@gmail.com",
    description="Unified RNA Analysis Toolkit - ML-powered RNA sequence analysis and structure prediction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/linorman/rnapy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="RNA bioinformatics machine-learning structure-prediction sequence-analysis",
    install_requires=requirements,
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "rnapy": [
            "configs/*.yaml",
            "configs/*.yml",
            "data/*",
        ],
    },
    entry_points={
        "console_scripts": [
            "rnapy=rnapy.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/linorman/rnapy/issues",
        "Source": "https://github.com/linorman/rnapy",
    },
)