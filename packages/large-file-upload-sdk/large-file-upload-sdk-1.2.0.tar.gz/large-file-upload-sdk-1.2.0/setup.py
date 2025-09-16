"""
File Upload SDK - Setup script
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="large-file-upload-sdk",
    version="1.2.0",
    author="SAIS Development Team",
    author_email="dev@sais.com.cn",
    description="Large File Upload SDK - Support chunked upload, resumable transfer, and Token authentication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/file-upload-server",
    project_urls={
        "Bug Reports": "https://github.com/your-username/file-upload-server/issues",
        "Documentation": "https://github.com/your-username/file-upload-server#readme",
        "Source": "https://github.com/your-username/file-upload-server",
    },
    py_modules=["file_upload_sdk"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="file upload, large file, chunked upload, resumable upload, file transfer, token authentication",
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
)
