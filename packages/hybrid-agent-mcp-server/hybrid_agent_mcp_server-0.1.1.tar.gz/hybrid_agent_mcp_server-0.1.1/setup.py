from setuptools import setup, find_packages

setup(
    name="hybrid-agent-mcp-server",
    version="0.1.1",
    description="MCP Server for Hybrid Agent Environment Management",
    author="Ki",
    packages=find_packages(),
    install_requires=[
        "mcp",
    ],
    entry_points={
        "console_scripts": [
            "hybrid-agent-mcp-server=hybrid_agent_mcp_server.main:main",
        ],
    },
    python_requires=">=3.8",
)
