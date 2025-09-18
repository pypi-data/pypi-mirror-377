from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aerodrome-swap-mcp",
    version="0.1.1",
    author="Aerodrome Swap Team",
    author_email="yi.zhou@netmind.ai",
    description="MCP server for Aerodrome Swap API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/protagolabs/aerodrome-swap-mcp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastmcp>=0.1.0",
        "requests>=2.28.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "aerodrome-swap-mcp=aerodrome_mcp.server:main",
        ],
    },
)
