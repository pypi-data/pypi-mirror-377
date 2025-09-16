# Hybrid Agent MCP Server

하이브리드 접근법을 위한 Agent 환경 준비 전용 MCP 서버

## 기능

- `prepare_agent_environment()`: Agent 실행용 가상환경 준비
- `prepare_agentcore_environment()`: AgentCore 배포용 가상환경 준비

## 특징

- 환경 설정만 담당 (실행은 안함)
- 경로 정보 반환 (Q CLI가 사용할 수 있도록)
- 최소한의 기능 (복잡성 제거)

## 사용법

```bash
pip install hybrid-agent-mcp-server
hybrid-agent-mcp-server
```
