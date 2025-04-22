from setuptools import setup, find_packages

setup(
    name="regen",
    version="0.1.0",
    description="A regex pattern generator with smart optimization",
    author="Thomas",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)