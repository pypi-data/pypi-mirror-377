'''
Autor: hy0506
Date: 2025-09-18 15:38:28
LastEditors: hy0506
LastEditTime: 2025-09-18 15:41:25
Description: heyu9504@163.com
'''
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="oss-internal-tool",
    version="1.7.3",
    author="Heyu007",
    author_email="610369073@qq.com",
    description="An internal utility package for Aliyun OSS operations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"}, 
    packages=find_packages(where="src"),
    install_requires=[
        "aiohappyeyeballs",
        "aiohttp",
        "aiosignal",
        "aliyun-python-sdk-core",
        "aliyun-python-sdk-kms",
        "asyncio-oss",
        "attrs",
        "certifi",
        "cffi",
        "charset-normalizer",
        "crcmod",
        "cryptography",
        "frozenlist",
        "idna",
        "jmespath",
        "multidict",
        "oss2",
        "propcache",
        "pycparser",
        "pycryptodome",
        "requests",
        "six",
        "tqdm",
        "urllib3",
        "yarl",
        "alibabacloud_oss_v2"
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    license="MIT",
    include_package_data=True
)
