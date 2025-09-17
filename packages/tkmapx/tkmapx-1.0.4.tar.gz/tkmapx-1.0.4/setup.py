from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tkmapx",
    version="1.0.4",
    author="Nebula Company",
    description="A Tkinter-based Python package for creating and visualizing simple maps with nodes and paths. (1.0.3 has other bug fixes, download this version)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Krishna-Developer5000/tkmap",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
)
