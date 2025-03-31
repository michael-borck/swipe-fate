from setuptools import setup, find_packages

setup(
    name="polysim",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "flet>=0.22.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "polysim=polysim.main:main",
        ],
    },
)