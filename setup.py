from setuptools import setup, find_packages

setup(
    name="shared_secret_authenticator",
    version="0.0.1",
    py_modules=['shared_secret_authenticator'],
    description="Shared Secret Authenticator password provider module for Matrix Synapse",
    include_package_data=True,
    zip_safe=True,
    install_requires=[],
)

