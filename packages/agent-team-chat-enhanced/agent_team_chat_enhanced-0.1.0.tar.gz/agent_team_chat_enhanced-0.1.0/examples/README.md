# Agent Team Chat Examples

This directory contains comprehensive examples demonstrating all features of the Agent Team Chat Enhanced MCP server.

## 🚀 Quick Start

Run any example with:
```bash
cd agent-team-chat-enhanced
python examples/demo_multi_agent.py
```

## 📋 Examples Overview

### 1. Multi-Agent Coordination Demo (`demo_multi_agent.py`)
**Complete end-to-end demonstration of team coordination**

Features demonstrated:
- ✅ Project creation and setup
- ✅ Multi-agent conversation with realistic roles
- ✅ Rate limiting and graceful handling
- ✅ Agent status/presence tracking
- ✅ Floor control for coordinated speaking
- ✅ Image sharing (base64)
- ✅ Documentation registration and search
- ✅ Project digest generation

**Run time:** ~30 seconds
**Prerequisites:** None (uses in-memory database)

```bash
python examples/demo_multi_agent.py
```

### 2. Webhook Receiver Example (`webhook_receiver_example.py`)
**Production-ready webhook receiver with HMAC verification**

Features demonstrated:
- ✅ HMAC-SHA256 signature verification
- ✅ Timestamp validation (replay attack prevention)
- ✅ Event type handling (message.created, status.updated, etc.)
- ✅ FastAPI web server for receiving webhooks
- ✅ Event logging and monitoring endpoints

**Run time:** Continuous server
**Prerequisites:** Agent Team Chat MCP server running

```bash
# Terminal 1: Start webhook receiver
python examples/webhook_receiver_example.py

# Terminal 2: Register webhook with your MCP server
# Use URL: http://127.0.0.1:8080/webhook
# Secret: your-webhook-secret-key
```

### 3. Documentation System Demo (`documentation_demo.py`)
**Comprehensive DocStation subsystem demonstration**

Features demonstrated:
- ✅ Text-based document registration
- ✅ URL-based document ingestion
- ✅ Automatic chunking for large documents
- ✅ Full-text search with FTS5
- ✅ Version management
- ✅ Chunk retrieval for detailed reading

**Run time:** ~15 seconds
**Prerequisites:** None (uses in-memory database)

```bash
python examples/documentation_demo.py
```

## 🎯 Integration Patterns

### MCP Client Configuration

Add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "agent-team-chat": {
      "command": "agent-team-chat",
      "args": []
    }
  }
}
```

### Environment Variables

Create `.env` file for configuration:

```bash
# Database and storage
ATC_DB_PATH=./data/agent_team_chat.db
ATC_IMAGE_DIR=./images

# Rate limiting (messages per interval)
ATC_RATE_LIMIT_CAPACITY=5
ATC_RATE_LIMIT_INTERVAL=60

# Logging
ATC_LOG_JSON=false
```

### Basic Usage Pattern

```python
from src.database import Database
from src.tools import ToolContext, create_project, send_message

# Setup
db = Database("./data.db")
ctx = ToolContext(db=db, image_dir="./images")

# Create project
project = create_project(ctx, name="My Team", description="Collaboration space")
project_id = project["project_id"]

# Send message
result = send_message(ctx,
    project_id=project_id,
    agent="agent_id",
    role="assistant",
    content="Hello team!")
```

## 🔧 Development and Testing

### Running All Tests

```bash
python -m unittest discover -s tests -v
```

### Manual Testing Steps

1. **Rate Limiting Test**
   ```bash
   # Send 6 rapid messages, expect 6th to be rate limited
   python -c "
   from examples.demo_multi_agent import *
   # ... test rate limiting code
   "
   ```

2. **Webhook Test**
   ```bash
   # Terminal 1
   python examples/webhook_receiver_example.py

   # Terminal 2
   python examples/demo_multi_agent.py
   # Check webhook receiver logs for events
   ```

3. **Documentation Search Test**
   ```bash
   python examples/documentation_demo.py
   # Verify search results are relevant and ranked properly
   ```

## 📊 Performance Characteristics

### Rate Limiting
- **Default capacity:** 5 messages per agent per project
- **Refill rate:** 1 message per 12 seconds (5 per 60 seconds)
- **Burst handling:** Allows temporary bursts within capacity
- **Graceful degradation:** Returns `retry_after` for smooth client handling

### Documentation System
- **Chunking:** 700-900 tokens per chunk (word-boundary aware)
- **Search:** FTS5 with porter stemming for intelligent matching
- **Storage:** SQLite with WAL mode for concurrent access
- **Performance:** Sub-second search on 10,000+ document chunks

### Webhook Delivery
- **Security:** HMAC-SHA256 signature with timestamp validation
- **Reliability:** 3 retry attempts with exponential backoff
- **Timeout:** 5-second timeout per webhook delivery
- **Concurrency:** Async delivery to multiple webhooks

## 🛡️ Security Features

### HMAC Signature Verification
```python
def verify_webhook_signature(timestamp, body, signature, secret):
    message = f"{timestamp}.".encode('utf-8') + body
    expected = hmac.new(secret.encode(), message, sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Input Validation
- File path sanitization prevents directory traversal
- Image validation (type, size limits)
- Message content length limits
- Agent ID and project ID validation

### Rate Limiting Protection
- Token bucket algorithm prevents spam
- Per-agent, per-project isolation
- Graceful handling with retry guidance

## 🔍 Monitoring and Observability

### Built-in Metrics
- Message throughput per agent/project
- Rate limit hit rates
- Webhook delivery success rates
- Document search query patterns
- Floor control usage statistics

### Logging
- Structured JSON logging available
- Configurable log levels
- Request/response tracking
- Error context preservation

### Health Checks
- Database connectivity
- Image directory accessibility
- Webhook endpoint validation
- Rate limiter state

## 💡 Tips for Production

1. **Database Setup**
   - Use WAL mode for better concurrency
   - Regular backups of SQLite database
   - Monitor database size growth

2. **Rate Limiting**
   - Adjust capacity based on team size
   - Monitor hit rates to tune limits
   - Consider per-project custom limits

3. **Webhook Reliability**
   - Use dedicated webhook endpoints
   - Implement proper error handling
   - Monitor delivery success rates

4. **Documentation Management**
   - Regular cleanup of old document versions
   - Monitor search query patterns
   - Optimize chunking for your content type

## 🚀 Next Steps

After running these examples:

1. Integrate with your preferred MCP client
2. Set up production database and storage
3. Configure webhooks for your workflow
4. Customize rate limiting for your team size
5. Import your team's existing documentation

For more advanced usage, see the main README.md and API documentation.