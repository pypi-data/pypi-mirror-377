from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="td-google-login",
    version="1.0.0",
    author="TD Solutions",
    author_email="support@td-solutions.com",
    description="A plug-and-play Django package for Google OAuth 2.0 authentication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/darshan-tbd/td-google-login",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=0.8.0",
        "google-auth-httplib2>=0.1.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-django>=4.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
