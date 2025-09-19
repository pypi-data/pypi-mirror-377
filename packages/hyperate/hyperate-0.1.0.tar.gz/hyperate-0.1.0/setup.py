from setuptools import setup, find_packages

setup(
    name="hyperate",
    version="0.1.0",
    description="Python client for the HypeRate WebSocket API",
    author="Serpensin",
    packages=find_packages(),
    install_requires=[
        "websockets>=10.0",
    ],
    python_requires=">=3.10",
    license="AGPL-3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    url="https://serpensin.com",
    project_urls={
        "Documentation": "https://github.com/Serpensin/HypeRate-Python#readme",
        "Source": "https://github.com/Serpensin/HypeRate-Python",
        "Homepage": "https://hyperate.io/"
    },
)