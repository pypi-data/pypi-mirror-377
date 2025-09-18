from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyqmt",
    version="1.0.4",
    author="量化交易汤姆猫",
    author_email="838993637@qq.com",
    description="A wrapper library for QMT_XTQUANT trading interface.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://quant0808.netlify.app",
    py_modules=["pyqmt"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.6",
    install_requires=[
        "xtquant",
        "tabulate",
        "schedule",
    ],
)