"""
AIShield - OWASP MCP Top 10 aligned security scanner for AI Agent tools
"""

from setuptools import setup, find_packages

setup(
    name="aishield",
    version="4.11.0",
    description="OWASP MCP Top 10 aligned security scanner for AI Agent tools",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="AIShield Team",
    license="MIT",
    packages=find_packages(exclude=["tests*", "mcp-server*", "node_modules*", "*.zip"]),
    python_requires=">=3.9",
    # 运行时服务器依赖（api.server 对外提供 L1 可移植身份 / L3 意图授权，
    # 二者建立在 Ed25519 上，必须 cryptography；scanner/policy.py 解析 YAML 配置
    # 需要 PyYAML）。注意：**不建 requirements.txt** —— ci.yml 的 dependency-check
    # 见到该文件直接 exit 1（守 scanner/runtime 零依赖对外承诺），测试依赖统一由
    # .github/actions/prepare-tests 声明并由 E12 派生校验。这里只钉运行时服务器
    # 真需要的依赖，让 `pip install -e .`（render / railway 部署）真正把依赖装上，
    # 而不是 `2>/dev/null; true` 把失败吞掉、生产静默降级成 hmac-sha256。
    install_requires=[
        "cryptography>=42.0.0",
        "PyYAML>=6.0",
    ],
    extras_require={
        "browser-use": ["browser-use>=0.2.0"],
        "graph-db": ["neo4j>=5.0.0"],
        "kafka": ["kafka-python>=2.0.0"],
        "all": [
            "browser-use>=0.2.0",
            "neo4j>=5.0.0",
            "kafka-python>=2.0.0",
        ],
    },
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
