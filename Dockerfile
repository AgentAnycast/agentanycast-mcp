FROM python:3.12-slim

LABEL maintainer="AgentAnycast Contributors"
LABEL description="AgentAnycast MCP Server — P2P agent networking for AI tools"

# Install agentanycast-mcp (pulls agentanycast SDK + daemon binary on first run)
RUN pip install --no-cache-dir agentanycast-mcp

# HTTP mode by default for containerized deployment
EXPOSE 8080

ENTRYPOINT ["agentanycast-mcp"]
CMD ["--transport", "http", "--port", "8080"]
