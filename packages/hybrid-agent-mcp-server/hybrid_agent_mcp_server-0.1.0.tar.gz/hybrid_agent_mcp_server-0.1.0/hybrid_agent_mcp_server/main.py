#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# MCP 서버 생성
mcp = FastMCP()

@mcp.tool()
def prepare_agent_environment(agent_path: str) -> dict:
    """
    Agent 실행을 위한 가상환경 준비 (환경 설정만, 실행은 안함)
    
    Args:
        agent_path: Agent 파일이 있는 디렉토리 경로
    
    Returns:
        dict: 가상환경 경로 정보
    """
    try:
        agent_path = Path(agent_path)
        venv_path = agent_path / "venv"
        
        # 가상환경 생성
        if not venv_path.exists():
            print(f"🔧 가상환경 생성: {venv_path}")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        # 가상환경 경로 설정
        if os.name == 'nt':  # Windows
            python_path = venv_path / "Scripts" / "python"
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix/Linux/macOS
            python_path = venv_path / "bin" / "python"
            pip_path = venv_path / "bin" / "pip"
        
        # 패키지 설치
        packages = [
            "strands-agents",
            "strands-agents-tools"
        ]
        
        for package in packages:
            print(f"📦 패키지 설치: {package}")
            subprocess.run([str(pip_path), "install", package], check=True)
        
        print("✅ 환경 준비 완료")
        
        return {
            "status": "success",
            "message": "Agent 환경 준비 완료",
            "venv_path": str(venv_path),
            "python_path": str(python_path),
            "pip_path": str(pip_path)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"환경 준비 중 오류: {str(e)}"
        }

@mcp.tool()
def prepare_agentcore_environment(agent_path: str) -> dict:
    """
    AgentCore 배포를 위한 가상환경 준비 (환경 설정만, 배포는 안함)
    
    Args:
        agent_path: Agent 파일이 있는 디렉토리 경로
    
    Returns:
        dict: AgentCore 환경 경로 정보
    """
    try:
        agent_path = Path(agent_path)
        agentcore_venv = agent_path / "agentcore-env"
        
        # AgentCore 가상환경 생성
        if not agentcore_venv.exists():
            print(f"🔧 AgentCore 가상환경 생성: {agentcore_venv}")
            subprocess.run([sys.executable, "-m", "venv", str(agentcore_venv)], check=True)
        
        # 가상환경 경로 설정
        if os.name == 'nt':  # Windows
            python_path = agentcore_venv / "Scripts" / "python"
            pip_path = agentcore_venv / "Scripts" / "pip"
            agentcore_path = agentcore_venv / "Scripts" / "agentcore"
        else:  # Unix/Linux/macOS
            python_path = agentcore_venv / "bin" / "python"
            pip_path = agentcore_venv / "bin" / "pip"
            agentcore_path = agentcore_venv / "bin" / "agentcore"
        
        # AgentCore 패키지 설치
        packages = [
            "bedrock-agentcore",
            "strands-agents",
            "bedrock-agentcore-starter-toolkit"
        ]
        
        for package in packages:
            print(f"📦 AgentCore 패키지 설치: {package}")
            subprocess.run([str(pip_path), "install", package], check=True)
        
        print("✅ AgentCore 환경 준비 완료")
        
        return {
            "status": "success",
            "message": "AgentCore 환경 준비 완료",
            "venv_path": str(agentcore_venv),
            "python_path": str(python_path),
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
