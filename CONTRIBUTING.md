# Contributing to Odoo Technical Support Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/technical-support-agent.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit: `git commit -m "Add: your feature description"`
7. Push: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

Follow the instructions in [README.md](README.md) to set up your development environment.

## Code Style

### Python

- Follow PEP 8 guidelines
- Use type hints where possible
- Maximum line length: 100 characters
- Use docstrings for functions and classes

Example:
```python
async def example_function(param: str) -> Dict[str, Any]:
    """
    Brief description of the function.

    Args:
        param: Description of parameter

    Returns:
        Description of return value
    """
    pass
```

### TypeScript/React

- Use TypeScript strict mode
- Follow functional component patterns
- Use Prettier for formatting (config in `.prettierrc`)
- Maximum line length: 100 characters

Example:
```typescript
interface Props {
  onConnect: (connected: boolean) => void;
}

export function Component({ onConnect }: Props) {
  // Implementation
}
```

## Commit Messages

Use conventional commits format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add user authentication tool
fix: resolve connection timeout issue
docs: update Railway deployment guide
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
pnpm test
```

## Adding New Features

### Adding an Agent Tool

1. Define the tool in `backend/agent/tools.py`
2. Add to the agent's tool list in `backend/agent/agent.py`
3. Add tests in `backend/tests/test_tools.py`
4. Update documentation

### Adding an MCP Tool

1. Implement in `backend/mcp/odoo_tools.py`
2. Register in `backend/mcp/server.py`
3. Add tests
4. Update MCP documentation

### Adding UI Components

1. Create component in `frontend/components/`
2. Follow existing patterns
3. Use TypeScript
4. Add to appropriate page
5. Test responsiveness

## Pull Request Guidelines

1. **One feature per PR**: Keep PRs focused on a single feature or fix
2. **Update documentation**: Include relevant documentation updates
3. **Add tests**: Include tests for new features
4. **Update CHANGELOG**: Add entry to CHANGELOG.md (if exists)
5. **Describe changes**: Provide clear description of what and why

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts
- [ ] Tested in development environment

## Reporting Issues

When reporting issues, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: How to reproduce the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Python version, Node version, etc.
6. **Logs**: Relevant error logs or stack traces

## Security Issues

**Do not** open public issues for security vulnerabilities. Instead, email security concerns to the maintainers.

## Questions?

Feel free to open a discussion or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
