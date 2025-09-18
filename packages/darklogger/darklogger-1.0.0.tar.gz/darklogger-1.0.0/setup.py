from setuptools import setup, find_packages
import os

# 读取README文件作为长描述
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="darklogger",
    version="1.0.0",
    author="jiruo",
    description="基于loguru的增强日志记录器，支持多实例、ID绑定和控制台输出控制",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "loguru>=0.6.0",
    ],
    keywords="logging logger loguru enhanced darklogger",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
