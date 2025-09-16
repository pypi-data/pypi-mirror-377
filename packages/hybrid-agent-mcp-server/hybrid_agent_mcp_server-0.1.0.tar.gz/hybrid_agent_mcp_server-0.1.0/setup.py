from setuptools import setup, find_packages

setup(
    name="hybrid-agent-mcp-server",
    version="0.1.0",
    author="Ki",
    description="하이브리드 접근법을 위한 Agent 환경 준비 전용 MCP 서버",
    long_description="Agent 실행을 위한 가상환경 준비만 담당하는 MCP 서버. 실제 실행은 Q CLI의 execute_bash로 실시간 피드백 제공.",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "hybrid-agent-mcp-server=hybrid_agent_mcp_server.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
