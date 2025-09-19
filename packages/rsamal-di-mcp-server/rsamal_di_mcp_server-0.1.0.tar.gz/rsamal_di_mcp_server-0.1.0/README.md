# Data Intelligence MCP Server

This project provides a modular, scalable Model Context Protocol (MCP) server designed for extensibility. It features a decorator-based registration system and a developer CLI to streamline the creation and management of new services and tools.

---

Table of Contents
-----------------

1. [Table of Contents](#table-of-contents)
2. [Quick Install - PyPI](#quick-install---pypi)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
3. [Quick Install - Container](#quick-install---container) *(Work in Progress)*
4. [Client](#client)
   - [Run in stdio mode from Claude/Copilot](#run-in-stdio-mode-from-claudecopilot)
   - [Run in http mode from Claude/Copilot](#run-in-http-mode-from-claudecopilot)
5. [Configuration](#configuration)
6. [Development](#development) *(Work in Progress)*

---

## Quick Install - PyPI

⚠️ **Public PyPI is not supported yet. Install is only supported through cloning the git repo.**

### Prerequisites
- Python 3.11 or higher

### Installation

Clone the repository:
```bash
git clone git@github.ibm.com:wdp-gov/data-intelligence-mcp-server.git
cd data-intelligence-mcp-server
```

Install globally using pypi package
```bash
make -f Makefile.local install-global
```
---

## Quick Install - Container

🚧 **Work in Progress**

Container-based installation options (Docker, Podman) will be documented here.

---

## Client

### Run in stdio mode from Claude/Copilot

⚠️ **Check [Configuration](#configuration) section below for all available configuration options**

Add the MCP server to your vscode copilot mcp configuration:
```json
{
  "servers": {
    "wxdi-mcp-server": {
      "command": "data-intelligence-mcp-server",
      "args": ["--transport", "stdio"],
      "env": {
         "BASE_URL" : "https://api.dataplatform.dev.cloud.ibm.com",
         "STDIO_AUTH_TOKEN" : "<bearer_token>"
      }
    }
  }
}
```

Add the MCP server to your claude desktop mcp config:
```json
{
  "mcpServers": {
    "wxdi-mcp-server": {
      "command": "data-intelligence-mcp-server",
      "args": ["--transport", "stdio"],
      "env": {
         "BASE_URL" : "https://api.dataplatform.dev.cloud.ibm.com",
         "STDIO_AUTH_TOKEN" : "<bearer_token>"
      }
    }
  }
}

```
### Run in http mode from Claude/Copilot

For HTTP mode, you'll need to start the server separately and then configure your client to connect to it.

#### Step 1: Start the MCP Server

Run the server in HTTP mode:
```bash
data-intelligence-mcp-server --transport http --host 0.0.0.0 --port 3000
```

#### Step 2: Configure Claude Desktop

Add the MCP server to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "wxdi-mcp-server": {
      "url": "http://localhost:3000/mcp",
      "env": {
        "BASE_URL": "https://api.dataplatform.dev.cloud.ibm.com",
        "STDIO_AUTH_TOKEN": "<bearer_token>"
      }
    }
  }
}
```

#### Step 3: Configure VS Code Copilot

Add the server to your VS Code Copilot MCP configuration:
```json
{
  "servers": {
    "wxdi-mcp-server": {
      "url": "http://localhost:3000/mcp",
      "env": {
        "BASE_URL": "https://api.dataplatform.dev.cloud.ibm.com",
        "STDIO_AUTH_TOKEN": "<bearer_token>"
      }
    }
  }
}
```

⚠️ **Note:** HTTP mode allows multiple clients to connect to the same server instance, but requires the server to be running continuously.



---

## Configuration

The MCP server can be configured using environment variables or a `.env` file. Copy `.env.example` to `.env` and modify the values as needed.

### Server Settings

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `SERVER_HOST` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `3000` | Server port number |
| `SERVER_TRANSPORT` | `http` | Transport protocol (`http` or `stdio`) |

### Authentication Settings

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `STDIO_AUTH_TOKEN` | `None` | Bearer token for stdio mode (optional) |
| `STDIO_API_KEY` | `None` | API key for authentication |
| `STDIO_USERNAME` | `None` | Username (required when using API key for CPD) |
| `ENV_MODE` | `SaaS` | Environment mode (`SaaS` or `CPD`) |

### HTTP Client Settings

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `REQUEST_TIMEOUT_S` | `30` | HTTP request timeout in seconds |
| `BASE_URL` | `None` | Base URL for Watson Data Platform instance |

### SSL/TLS Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `SSL_VERIFY` | `true` | Enable/disable SSL certificate verification |
| `AUTH_MODE` | `disabled` | Authentication mode (`disabled`, `bypass`, `jwt`, `cpd`) |
| `AUTH_IAM_URL` | `None` | IAM service URL for JWT mode |
| `AUTH_WKC_SERVICE_ID` | `None` | Base64 encoded credentials for CPD mode |
| `AUTH_AUTO_ERROR` | `true` | Automatically return errors on auth failures |

### SSL Certificate Modes

The server supports different SSL certificate verification modes:

- **`system_default`**: Use system CA certificate store (default)
- **`custom_ca_bundle`**: Use custom CA certificate bundle file
- **`client_cert`**: Client certificate authentication (mutual TLS)
- **`disabled`**: Disable SSL certificate verification

### Example Configurations

#### Development Environment
```bash
# .env
SERVER_TRANSPORT=http
AUTH_MODE=disabled
SSL_VERIFY=false
BASE_URL=https://your-dev-instance.cloud.ibm.com
```

#### Production Environment (SaaS)
```bash
# .env
SERVER_TRANSPORT=stdio
ENV_MODE=SaaS
AUTH_MODE=jwt
SSL_VERIFY=true
BASE_URL=https://your-prod-instance.cloud.ibm.com
STDIO_AUTH_TOKEN=your-bearer-token-here
```

#### Production Environment (CPD)
```bash
# .env
SERVER_TRANSPORT=stdio
ENV_MODE=CPD
AUTH_MODE=cpd
SSL_VERIFY=true
BASE_URL=https://your-cpd-cluster.com
STDIO_USERNAME=your-username
STDIO_APIKEY=your-api-key
```

---

## Development

🚧 **Work in Progress**

Development setup, contribution guidelines, and local development instructions will be documented here.

### Coming Soon:
- Local development environment setup
- Contributing guidelines
- Code style and testing requirements
- Service and tool development guides
