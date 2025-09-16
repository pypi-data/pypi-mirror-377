#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# MCP 서버 초기화 시 가상환경 설정
def setup_environment():
    """MCP 서버 시작 시 가상환경 생성 및 패키지 설치"""
    venv_path = Path.home() / ".hybrid-agent-mcp-venv"
    
    if not venv_path.exists():
        print(f"Creating virtual environment at {venv_path}")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        # 가상환경의 pip 경로
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix/Linux/macOS
            pip_path = venv_path / "bin" / "pip"
        
        # 필요한 패키지 설치
        packages = [
            "strands-agents",
            "strands-agents-tools",
            "bedrock-agentcore"
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            subprocess.run([str(pip_path), "install", package], check=True)
        
        print("Environment setup complete!")
    
    return venv_path

# 가상환경 설정
VENV_PATH = setup_environment()

# MCP 서버 생성
mcp = FastMCP()

@mcp.tool()
def prepare_agent_environment(
    agent_path: str
) -> dict:
    """
    Agent 실행을 위한 환경 정보 반환 (MCP 서버의 가상환경 사용)
    
    Args:
        agent_path: Agent 파일이 있는 디렉토리 경로 (예: "~/s3_bucket_query-agent")
    
    Returns:
        dict: 환경 정보
    """
    try:
        # 경로 확장 (~ 처리)
        agent_path = os.path.expanduser(agent_path)
        agent_dir = Path(agent_path)
        
        # 디렉토리가 존재하는지 확인
        if not agent_dir.exists():
            return {
                "status": "error",
                "message": f"Agent 디렉토리가 존재하지 않습니다: {agent_path}"
            }
        
        # MCP 서버의 가상환경 경로
        if os.name == 'nt':  # Windows
            python_path = VENV_PATH / "Scripts" / "python"
        else:  # Unix/Linux/macOS
            python_path = VENV_PATH / "bin" / "python"
        
        return {
            "status": "success",
            "message": "Agent 환경 준비 완료 (MCP 서버 가상환경 사용)",
            "agent_path": str(agent_dir),
            "venv_path": str(VENV_PATH),
            "python_path": str(python_path)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"환경 준비 중 오류: {str(e)}"
        }

@mcp.tool()
def prepare_agentcore_environment(
    agent_path: str
) -> dict:
    """
    AgentCore 배포를 위한 환경 준비 (별도 agentcore-env 생성)
    
    Args:
        agent_path: Agent 파일이 있는 디렉토리 경로
    
    Returns:
        dict: 환경 설정 결과
    """
    try:
        # 경로 확장 (~ 처리)
        agent_path = os.path.expanduser(agent_path)
        agent_dir = Path(agent_path)
        
        # agentcore-env 가상환경 생성 (배포용)
        agentcore_venv = agent_dir / "agentcore-env"
        
        if not agentcore_venv.exists():
            subprocess.run([sys.executable, "-m", "venv", str(agentcore_venv)], check=True)
        
        # pip 경로 설정
        if os.name == 'nt':  # Windows
            pip_path = agentcore_venv / "Scripts" / "pip"
            agentcore_path = agentcore_venv / "Scripts" / "agentcore"
        else:  # Unix/Linux/macOS
            pip_path = agentcore_venv / "bin" / "pip"
            agentcore_path = agentcore_venv / "bin" / "agentcore"
        
        # AgentCore 패키지 설치
        packages = [
            "bedrock-agentcore",
            "bedrock-agentcore-starter-toolkit",
            "strands-agents",
            "strands-agents-tools"
        ]
        
        for package in packages:
            subprocess.run([str(pip_path), "install", package], check=True)
        
        return {
            "status": "success",
            "message": "AgentCore 환경 준비 완료",
            "agent_path": str(agent_dir),
            "agentcore_venv_path": str(agentcore_venv),
            "agentcore_path": str(agentcore_path)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"AgentCore 환경 준비 중 오류: {str(e)}"
        }

def main():
    """MCP 서버 실행"""
    mcp.run()

if __name__ == "__main__":
    main()
