from setuptools import setup, find_packages

setup(
    name="jndataset-down",
    version="0.7.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "tqdm",
        "click",
        "psutil",
        "filelock",
        "pytz"
    ],
    entry_points={
        "console_scripts": [
            "jndataset-down = dataset_down.cli:main",  # 命令行入口
        ],
    },
    author="",
    author_email="your.email@example.com",
    description="A SDK for file downloading with resumable and multi-threaded features.",
    long_description=open("README.md",encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/****",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)