# Stack Overflow MCP Server

A Model Context Protocol (MCP) server that provides comprehensive tools for interacting with Stack Overflow through the Stack Exchange API. This server enables AI assistants to search questions, get detailed answers, and explore Stack Overflow content through a standardized interface.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.10.6+-green.svg)](https://github.com/jlowin/fastmcp)

## 🚀 Features

- **Question Search** - Advanced search with multiple filters and sorting options
- **Question Details** - Get comprehensive information including answers and comments
- **Answer Search** - Find and retrieve detailed answer information
- **Tag Support** - Search questions by specific tags
- **Type Safety** - Full Pydantic validation for all inputs
- **Error Handling** - Comprehensive error reporting and logging

## 📦 Installation

### Using uvx (Recommended)

```bash
uvx stack-overflow-mcp-light
```

### Using uv

```bash
uv add stack-overflow-mcp-light
uv run stack-overflow-mcp-light
```

### Using pip

```bash
pip install stack-overflow-mcp-light
stack-overflow-mcp-light
```

## ⚙️ Configuration

### Environment Variables

Configure the following environment variables:

```bash
# Optional: Stack Exchange API key for higher rate limits
export STACK_EXCHANGE_API_KEY="your_api_key_here"

# Optional: Show detailed logs for debugging (default: false)
export STACK_OVERFLOW_MCP_SHOW_LOGS="false"
```

> 💡 **API Key**: While optional, an API key significantly increases your rate limits from 300 to 10,000 requests per day.

#### Environment Variable Details

- **`STACK_EXCHANGE_API_KEY`** (Optional): Your Stack Exchange API key for increased rate limits. Get one at [Stack Apps](https://stackapps.com/apps/oauth/register)
- **`STACK_OVERFLOW_MCP_SHOW_LOGS`** (Optional): Set to `"true"` to enable detailed logging for debugging and development

### Claude Desktop Configuration

Add to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "stack-overflow": {
      "command": "uvx",
      "args": ["--no-progress", "stack-overflow-mcp-light"],
      "env": {
        "STACK_EXCHANGE_API_KEY": "your_api_key_here",
        "STACK_OVERFLOW_MCP_SHOW_LOGS": "false"
      },
      "transport": "stdio"
    }
  }
}
```

### Alternative Configurations

#### Using uv directly:
```json
{
  "mcpServers": {
    "stack-overflow": {
      "command": "uv",
      "args": ["run", "--with", "stack-overflow-mcp-light", "stack-overflow-mcp-light"],
      "env": {
        "STACK_EXCHANGE_API_KEY": "your_api_key_here",
        "STACK_OVERFLOW_MCP_SHOW_LOGS": "false"
      },
      "transport": "stdio"
    }
  }
}
```

#### Local development:
```json
{
  "mcpServers": {
    "stack-overflow": {
      "command": "uv",
      "args": ["run", "stack-overflow-mcp-light"],
      "cwd": "/path/to/stack-overflow-mcp-light",
      "env": {
        "STACK_EXCHANGE_API_KEY": "your_api_key_here",
        "STACK_OVERFLOW_MCP_SHOW_LOGS": "true"
      },
      "transport": "stdio"
    }
  }
}
```

## 🛠️ Available Tools

### ❓ Question Tools (4 tools)

#### `search_questions`
Search Stack Overflow questions with advanced filters.
- **Input**: Search parameters including:
  - `q` - Free-form text search
  - `tagged` - Semi-colon delimited list of tags
  - `intitle` - Search in question titles
  - `nottagged` - Exclude these tags
  - `body` - Text in question body
  - `accepted` - Has accepted answer (boolean)
  - `closed` - Question is closed (boolean)
  - `answers` - Minimum number of answers
  - `views` - Minimum view count
  - `sort` - Sort criteria ("activity", "votes", "creation", "hot", "week", "month", "relevance")
  - `order` - Sort order ("asc" or "desc")
  - `page` - Page number (1-25)
  - `page_size` - Items per page (1-100)
- **Output**: Search results with questions matching criteria

#### `get_question_details`
Get detailed information about a specific question.
- **Input**: `question_id`, `include_body` (boolean), `include_comments` (boolean), `include_answers` (boolean)
- **Output**: Comprehensive question information including body, answers, and optionally comments

#### `get_questions_by_tag`
Get questions that have a specific tag.
- **Input**: `tag` (tag name), `sort`, `order`, `page`, `page_size`
- **Output**: Questions with the specified tag

#### `get_question_answers`
Get answers for a specific question.
- **Input**: `question_id`
- **Output**: All answers for the specified question

### 💬 Answer Tools (3 tools)

#### `search_answers`
Search Stack Overflow answers using text search.
- **Input**: `q` (optional search query), `sort`, `order`, `page`, `page_size`
- **Output**: Search results with answers matching the query

#### `get_answer_details`
Get detailed information about a specific answer.
- **Input**: `answer_id`, `include_body` (boolean), `include_comments` (boolean)
- **Output**: Detailed answer information including body and optionally comments

#### `get_top_answers`
Get top-voted answers from Stack Overflow.
- **Input**: None (uses default sorting by votes)
- **Output**: Top answers sorted by vote count

## 🧪 Testing

The project includes comprehensive tests covering all tools:

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test categories
uv run pytest tests/test_server.py::TestQuestionTools -v
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/midodimori/stack-overflow-mcp-light.git
cd stack-overflow-mcp-light

# Install with development dependencies
make install-dev

# Run tests
make test

# Format and lint code
make format

# Check code style and types
make lint

# Run the server locally
make run

# See all available commands
make help
```

### Project Structure

```
stack-overflow-mcp-light/
├── src/stack_overflow_mcp_light/
│   ├── __init__.py
│   ├── server.py          # MCP server implementation
│   ├── models.py          # Pydantic models
│   ├── logging_config.py  # Logging configuration
│   └── tools/             # Tool implementations
│       ├── __init__.py
│       ├── base_client.py # Base client for Stack Exchange API
│       ├── questions.py   # Question search and retrieval tools
│       └── answers.py     # Answer search and retrieval tools
├── tests/
│   ├── test_server.py     # Tool function tests
│   └── test_mcp_integration.py  # MCP integration tests
├── pyproject.toml         # Project configuration
└── README.md
```

## 📚 API Reference

### Question Sort Options
- **activity**: Sort by last activity date (default)
- **votes**: Sort by question score
- **creation**: Sort by creation date
- **hot**: Sort by current hotness
- **week**: Sort by weekly activity
- **month**: Sort by monthly activity
- **relevance**: Sort by search relevance

### Answer Sort Options
- **activity**: Sort by last activity date (default)
- **votes**: Sort by answer score
- **creation**: Sort by creation date

### Sort Order
- **desc**: Descending order (default)
- **asc**: Ascending order

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is provided for educational and informational purposes only. This tool interacts with Stack Overflow's public API and respects their rate limits and terms of service. The authors are not responsible for any misuse of the Stack Exchange API or violation of their terms of service.

## 🔗 Links

- [Stack Overflow](https://stackoverflow.com/)
- [Stack Exchange API Documentation](https://api.stackexchange.com/docs)
- [Stack Apps - API Key Registration](https://stackapps.com/apps/oauth/register)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Claude Desktop](https://claude.ai/desktop)

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the [Stack Overflow Meta](https://meta.stackoverflow.com/) for API-related questions
- Review the comprehensive test suite for usage examples