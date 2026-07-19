"""
AIShield - OWASP MCP Top 10 aligned security scanner for AI Agent tools
"""

from setuptools import setup, find_packages

setup(
    name="aishield",
    version="4.1.0",
    description="OWASP MCP Top 10 aligned security scanner for AI Agent tools",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="AIShield Team",
    license="MIT",
    packages=find_packages(exclude=["tests*", "mcp-server*", "node_modules*", "*.zip"]),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "aishield=api.server:main",
            "aishield-api=api.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
    ],
)
