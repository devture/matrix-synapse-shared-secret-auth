from setuptools import setup, find_packages

setup(
    name="shared_secret_authenticator",
    version="2.0.1",
    py_modules=['shared_secret_authenticator'],
    description="Shared Secret Authenticator password provider module for Matrix Synapse",
    include_package_data=True,
    zip_safe=True,
    install_requires=['matrix-synapse>=1.46'],
    python_requires="~=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)

