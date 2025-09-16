from setuptools import setup, find_packages

setup(
    name="ki.aws-strands-agentcore-venv-mcp-server",
    version="0.1.8",
    description="MCP Server for AWS Strands AgentCore Virtual Environment Management",
    author="Ki",
    packages=find_packages(),
    install_requires=[
        "mcp",
    ],
    entry_points={
        "console_scripts": [
            "ki-aws-strands-agentcore-venv-mcp-server=ki_aws_strands_agentcore_venv_mcp_server.main:main",
        ],
    },
    python_requires=">=3.8",
)
