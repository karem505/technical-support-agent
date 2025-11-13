# MCP (Model Context Protocol) Integration

This document explains how the Odoo Technical Support Agent uses MCP for standardized AI-Odoo interactions.

## What is MCP?

Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). It enables:

- Standardized tool definitions
- Consistent data access patterns
- Reusable AI integrations
- Better separation of concerns

## Architecture

```
┌─────────────────┐
│  Voice Agent    │
│  (OpenAI)       │
└────────┬────────┘
         │
         │ Uses Tools
         ▼
┌─────────────────┐
│  Agent Tools    │
│  (Python)       │
└────────┬────────┘
         │
         │ Calls MCP
         ▼
┌─────────────────┐
│  MCP Server     │
│  (Protocol)     │
└────────┬────────┘
         │
         │ Connects to
         ▼
┌─────────────────┐
│  Odoo Instance  │
│  (XML-RPC)      │
└─────────────────┘
```

## MCP Server Implementation

The MCP server (`backend/mcp/server.py`) provides standardized access to Odoo:

### Available Tools

#### 1. Module Management

**list_modules**
- Description: List all Odoo modules
- Input: None
- Output: Array of modules with state and version

```json
{
  "name": "list_modules"
}
```

**get_module_info**
- Description: Get detailed module information
- Input: `module_name` (string)
- Output: Module details

```json
{
  "name": "get_module_info",
  "arguments": {
    "module_name": "sale"
  }
}
```

**check_module_dependencies**
- Description: Check module dependencies
- Input: `module_name` (string)
- Output: List of dependencies

#### 2. User Management

**list_users**
- Description: List all users
- Input: None
- Output: Array of users

**get_user_details**
- Description: Get user details
- Input: `user_id` (integer)
- Output: User information

```json
{
  "name": "get_user_details",
  "arguments": {
    "user_id": 2
  }
}
```

#### 3. Data Access

**search_records**
- Description: Search records in any model
- Input:
  - `model` (string): Model name
  - `domain` (array): Odoo domain
  - `fields` (array, optional): Fields to retrieve

```json
{
  "name": "search_records",
  "arguments": {
    "model": "res.partner",
    "domain": [["is_company", "=", true]],
    "fields": ["name", "email", "phone"]
  }
}
```

#### 4. System Information

**get_database_info**
- Description: Get database information
- Input: None
- Output: Database details

**get_company_info**
- Description: Get company information
- Input: None
- Output: Company details

## Using the MCP Server

### Standalone Mode

Run the MCP server independently:

```bash
cd backend
python -m mcp.server
```

This starts the server in stdio mode, ready to accept MCP protocol messages.

### Integration with Agent

The agent automatically uses MCP tools through the `OdooTools` class:

```python
from agent.tools import OdooTools

tools = OdooTools()

# Tools are automatically registered with the agent
result = await tools.get_installed_modules()
```

## Adding New MCP Tools

### 1. Define the Tool in odoo_tools.py

```python
async def your_new_tool(self, param: str) -> Dict[str, Any]:
    """Your tool description"""
    try:
        odoo = self.connect()
        # Your implementation
        result = ...
        return result
    except Exception as e:
        logger.error(f"Error in your_new_tool: {e}")
        return {"error": str(e)}
```

### 2. Register in server.py

Add to `list_tools()`:

```python
Tool(
    name="your_new_tool",
    description="What your tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {
                "type": "string",
                "description": "Parameter description",
            }
        },
        "required": ["param"],
    },
)
```

Add to `call_tool()`:

```python
elif name == "your_new_tool":
    result = await odoo_tools.your_new_tool(arguments["param"])
```

### 3. Expose in Agent Tools

Add to `agent/tools.py`:

```python
@llm.ai_callable(
    description="What your tool does"
)
async def your_new_tool(
    self,
    param: Annotated[str, llm.TypeInfo(description="Parameter description")]
) -> str:
    """Your tool implementation"""
    # Call MCP server or implement directly
    pass
```

## Best Practices

### 1. Error Handling

Always wrap MCP calls in try-except:

```python
try:
    result = await odoo_tools.some_operation()
except Exception as e:
    logger.error(f"MCP operation failed: {e}")
    return {"error": str(e)}
```

### 2. Connection Management

The MCP tools handle connection pooling:

```python
# Connection is established on first use
odoo = self.connect()

# Reused for subsequent calls
# ...

# Cleanup when done
self.disconnect()
```

### 3. Type Safety

Use Pydantic models for complex inputs:

```python
from pydantic import BaseModel

class SearchRequest(BaseModel):
    model: str
    domain: List[List]
    fields: Optional[List[str]] = None

async def search_records(self, request: SearchRequest):
    # Implementation with validated input
    pass
```

### 4. Logging

Log all MCP operations for debugging:

```python
logger.info(f"MCP call: {tool_name} with args: {arguments}")
result = await tool_function(**arguments)
logger.info(f"MCP result: {result}")
```

## Security Considerations

### 1. Authentication

- MCP server uses Odoo credentials from environment
- Never expose credentials in tool responses
- Use service accounts with minimal permissions

### 2. Input Validation

Always validate inputs before passing to Odoo:

```python
def validate_domain(domain: List) -> bool:
    """Validate Odoo domain format"""
    if not isinstance(domain, list):
        return False
    # Additional validation
    return True
```

### 3. Rate Limiting

Implement rate limiting for expensive operations:

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
async def cached_operation(key: str):
    # Expensive operation
    pass
```

### 4. Audit Trail

Log all operations for security auditing:

```python
logger.info(
    f"User {user_id} executed {operation} "
    f"on model {model} at {datetime.now()}"
)
```

## Testing MCP Tools

### Unit Tests

Create tests in `backend/tests/test_mcp.py`:

```python
import pytest
from mcp.odoo_tools import OdooMCPTools

@pytest.mark.asyncio
async def test_list_modules():
    tools = OdooMCPTools()
    result = await tools.list_modules()
    assert isinstance(result, list)
    assert len(result) > 0
```

### Integration Tests

Test with real Odoo instance:

```python
@pytest.mark.integration
async def test_create_user():
    tools = OdooMCPTools()
    result = await tools.create_user(
        name="Test User",
        login="testuser",
        email="test@example.com"
    )
    assert "error" not in result
```

### Manual Testing

Use the MCP CLI:

```bash
# Install MCP CLI
pip install mcp-cli

# Test tool
mcp-cli call \
  --server "python -m mcp.server" \
  --tool list_modules
```

## Performance Optimization

### 1. Caching

Cache frequently accessed data:

```python
from functools import lru_cache
from asyncio import sleep

@lru_cache(maxsize=128)
async def get_module_info(module_name: str):
    # Result is cached
    pass
```

### 2. Batch Operations

Batch multiple requests:

```python
async def batch_search(requests: List[SearchRequest]):
    """Process multiple searches efficiently"""
    tasks = [self.search_records(req) for req in requests]
    results = await asyncio.gather(*tasks)
    return results
```

### 3. Connection Pooling

Reuse Odoo connections:

```python
class ConnectionPool:
    def __init__(self, max_connections=5):
        self.pool = []
        self.max_connections = max_connections

    async def get_connection(self):
        # Return available or create new
        pass
```

## Monitoring

### Metrics to Track

1. **Tool Usage**
   - Call frequency per tool
   - Success/failure rates
   - Average execution time

2. **Error Rates**
   - Connection failures
   - Authentication errors
   - Odoo API errors

3. **Performance**
   - Response times
   - Query complexity
   - Resource usage

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp.log'),
        logging.StreamHandler()
    ]
)
```

## Troubleshooting

### Common Issues

**Connection Refused**
```
Error: [Errno 111] Connection refused
```
- Check Odoo is running and accessible
- Verify host and port in configuration

**Authentication Failed**
```
Error: Access Denied
```
- Check username and password
- Verify user has required permissions

**Model Not Found**
```
Error: Model 'xyz' does not exist
```
- Check model name spelling
- Verify module providing the model is installed

## Resources

- MCP Specification: https://modelcontextprotocol.io
- Odoo XML-RPC Documentation: https://www.odoo.com/documentation/16.0/developer/misc/api/odoo.html
- OdooRPC Library: https://github.com/OCA/odoorpc

## Future Enhancements

Planned MCP features:

1. **Streaming Responses**: For large datasets
2. **Webhook Support**: For real-time updates
3. **Advanced Caching**: Redis-based distributed cache
4. **Multi-tenant Support**: Multiple Odoo instances
5. **GraphQL Interface**: Alternative to MCP protocol
