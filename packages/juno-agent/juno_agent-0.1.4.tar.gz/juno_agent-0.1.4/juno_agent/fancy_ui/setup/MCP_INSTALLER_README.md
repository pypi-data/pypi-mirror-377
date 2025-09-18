# MCP Server Installation Service

The MCP (Model Context Protocol) Installer service provides comprehensive support for installing and configuring MCP servers across different AI IDEs, with a special focus on the VibeContext MCP server.

## Overview

The `MCPInstaller` class is a cross-platform service that can:

- Install MCP servers for multiple AI IDEs
- Configure the VibeContext MCP server with proper settings
- Preserve existing MCP server configurations
- Provide validation and error handling
- Support environment variable configuration

## Supported AI IDEs

| IDE | Config Location | File Pattern |
|-----|----------------|--------------|
| **Claude Code** | `~/.claude_code_config.json` | Home directory |
| **Cursor** | `.cursor/mcp.json` | Project directory |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` | Windsurf home |
| **VS Code** | `.vscode/mcp.json` | Project directory |

## VibeContext MCP Server Configuration

The service automatically configures the VibeContext MCP server with:

```json
{
  "vibe_context": {
    "command": "node" | "npx",
    "args": ["/path/to/build/index.js"] | ["-y", "askbudi-context@latest"],
    "env": {
      "ASKBUDI_API_KEY": "your_api_key",
      "PLATFORM": "claude"
    },
    "_metadata": {
      "description": "VibeContext MCP Server - Provides library documentation and code analysis",
      "capabilities": [
        "File structure analysis using Universal Ctags",
        "Library documentation access with search",
        "URL fetching and markdown conversion",
        "Code snippet extraction and analysis"
      ],
      "version": "1.0.4"
    }
  }
}
```

## Basic Usage

### Installation

```python
from py_wizard_cli.fancy_ui.setup import MCPInstaller, MCPInstallationError
from pathlib import Path

# Initialize the installer
installer = MCPInstaller()

# Install for Claude Code
project_path = Path.cwd()
api_key = "your_vibe_context_api_key"

try:
    success = installer.install_mcp_servers("claude_code", project_path, api_key)
    if success:
        print("✅ Installation successful!")
    else:
        print("❌ Installation failed")
except MCPInstallationError as e:
    print(f"❌ Installation error: {e}")
```

### Convenience Functions

```python
from py_wizard_cli.fancy_ui.setup import (
    install_vibe_context_for_editor,
    get_supported_editors,
    get_editor_display_names
)

# Quick installation
success = install_vibe_context_for_editor("cursor", Path.cwd(), "your_api_key")

# Get supported editors
editors = get_supported_editors()  # ['claude_code', 'cursor', 'windsurf', 'vscode']

# Get display names
names = get_editor_display_names()  # {'claude_code': 'Claude Code', ...}
```

## Advanced Usage

### Check Installation Status

```python
# Get detailed installation status
status = installer.get_installation_status("claude_code")

print(f"Config exists: {status['config_exists']}")
print(f"VibeContext installed: {status['vibe_context_installed']}")
print(f"Total servers: {status['total_servers']}")
print(f"Config path: {status['config_path']}")
```

### List Installed Servers

```python
# List all installed MCP servers
servers = installer.list_installed_servers("cursor", project_path)

for server in servers:
    print(f"📦 {server['name']}")
    print(f"   Command: {server['command']}")
    print(f"   Args: {server['args']}")
    print(f"   Env vars: {', '.join(server['env_vars'])}")
```

### Remove MCP Servers

```python
# Remove a specific MCP server
success = installer.remove_mcp_server("claude_code", "vibe_context")
if success:
    print("✅ Server removed successfully")
```

### API Key Validation

```python
# Validate API key format
api_key = "vibe_your_key_here"
valid, message = installer.validate_api_key(api_key)

if valid:
    print(f"✅ {message}")
else:
    print(f"❌ {message}")
```

### Configuration Path Management

```python
# Get configuration paths for different editors
editors = get_supported_editors()

for editor in editors:
    try:
        config_path = installer.get_mcp_config_path(editor, project_path)
        print(f"{editor}: {config_path}")
    except MCPInstallationError as e:
        print(f"{editor}: Error - {e}")
```

## Key Features

### 🔄 Cross-Platform Compatibility

The installer works across different operating systems and handles platform-specific path conventions automatically.

### 🛡️ Configuration Preservation

When installing new MCP servers, existing configurations are preserved and merged appropriately.

### 📁 Automatic Path Detection

The service automatically detects local VibeContext server builds and falls back to npm packages when needed.

### 🔧 Environment Variable Support

Full support for environment variable configuration, including secure API key handling.

### 📊 Comprehensive Logging

Built-in logging for debugging installation issues and tracking configuration changes.

### ⚡ Error Handling

Robust error handling with specific exception types for different failure modes.

## VibeContext Server Capabilities

The installed VibeContext MCP server provides:

### 📋 File Structure Analysis
- Uses Universal Ctags for code analysis
- Supports multiple programming languages
- Generates hierarchical symbol trees
- Provides line range information

### 📚 Library Documentation Access
- Search and retrieve documentation for popular libraries
- Up-to-date information from official sources
- Context-aware code examples
- API reference integration

### 🌐 URL Fetching and Processing
- Fetch documentation from web URLs
- Convert HTML to clean markdown
- Handle GitHub repository documentation
- Cache responses for performance

### 🔍 Code Analysis Tools
- Extract code snippets with context
- Analyze project structure
- Support for multiple file formats
- Integration with development workflows

## Configuration Examples

### Claude Code Configuration

Location: `~/.claude_code_config.json`

```json
{
  "mcpServers": {
    "vibe_context": {
      "command": "node",
      "args": ["/path/to/VibeContext/ts_mcp_server/build/index.js"],
      "env": {
        "ASKBUDI_API_KEY": "vibe_your_api_key_here",
        "PLATFORM": "claude"
      }
    }
  }
}
```

### Cursor Configuration

Location: `.cursor/mcp.json` (in project directory)

```json
{
  "mcpServers": {
    "vibe_context": {
      "command": "npx",
      "args": ["-y", "askbudi-context@latest"],
      "env": {
        "ASKBUDI_API_KEY": "vibe_your_api_key_here",
        "PLATFORM": "claude"
      }
    }
  }
}
```

### VS Code Configuration

Location: `.vscode/mcp.json` (in project directory)

```json
{
  "mcpServers": {
    "vibe_context": {
      "command": "npx",
      "args": ["-y", "askbudi-context@latest"],
      "env": {
        "ASKBUDI_API_KEY": "vibe_your_api_key_here",
        "PLATFORM": "claude"
      }
    }
  }
}
```

### Windsurf Configuration

Location: `~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "vibe_context": {
      "command": "npx",
      "args": ["-y", "askbudi-context@latest"],
      "env": {
        "ASKBUDI_API_KEY": "vibe_your_api_key_here",
        "PLATFORM": "claude"
      }
    }
  }
}
```

## Error Handling

The service provides specific error types for different scenarios:

### MCPInstallationError

Raised when installation operations fail:

```python
try:
    installer.install_mcp_servers("unsupported_editor", path, api_key)
except MCPInstallationError as e:
    print(f"Installation failed: {e}")
```

### Common Error Scenarios

1. **Unsupported Editor**: When trying to install for an editor that isn't supported
2. **Invalid API Key**: When the provided API key doesn't meet validation criteria
3. **Path Issues**: When configuration directories can't be created or accessed
4. **JSON Errors**: When existing configuration files have invalid JSON syntax
5. **Permission Issues**: When the installer doesn't have write access to config files

## Testing

The service includes comprehensive test coverage:

```bash
# Run the test suite
cd py_wizard_cli/fancy_ui/setup
python test_mcp_installer.py
```

### Test Coverage

- ✅ Configuration path generation
- ✅ API key validation
- ✅ VibeContext configuration creation
- ✅ IDE configuration updates
- ✅ Server listing and removal
- ✅ Installation status checking
- ✅ Error handling scenarios
- ✅ Integration workflows

## Interactive Demo

Run the interactive demo to explore functionality:

```bash
cd py_wizard_cli/fancy_ui/setup
python example_mcp_installer_usage.py
```

The demo provides:

1. 📝 Editor Selection
2. 🔑 API Key Validation
3. 📂 Configuration Path Check
4. 📊 Installation Status
5. 📋 List Installed Servers
6. 🚀 Full Installation Demo
7. 🗑️ Server Removal Demo

## Integration with TUI Application

The MCP installer integrates seamlessly with the existing TUI application:

```python
from py_wizard_cli.fancy_ui.setup import MCPInstaller

class SetupScreen(Screen):
    """Setup screen with MCP installation support."""
    
    def __init__(self):
        super().__init__()
        self.mcp_installer = MCPInstaller()
    
    def install_mcp_for_selected_editor(self, editor: str, api_key: str):
        """Install MCP servers for the selected editor."""
        try:
            success = self.mcp_installer.install_mcp_servers(
                editor, Path.cwd(), api_key
            )
            if success:
                self.notify("✅ MCP servers installed successfully!")
            else:
                self.notify("❌ MCP installation failed", severity="error")
        except MCPInstallationError as e:
            self.notify(f"❌ Installation error: {e}", severity="error")
```

## Best Practices

### 🔐 API Key Security

- Store API keys securely using environment variables
- Validate API keys before installation
- Never commit API keys to version control

### 📂 Configuration Management

- Always backup existing configurations before modifications
- Use atomic updates to prevent partial configurations
- Validate JSON structure after updates

### 🔄 Cross-Platform Support

- Use `pathlib.Path` for all path operations
- Handle platform-specific directory structures
- Test on multiple operating systems

### 📊 Logging and Monitoring

- Enable logging for debugging installation issues
- Monitor configuration file changes
- Track API key usage and validation

## Troubleshooting

### Common Issues

**Q: Installation fails with "Permission denied" error**
A: Ensure the user has write permissions to the configuration directory. For home directory configs, check user permissions. For project configs, ensure the project directory is writable.

**Q: VibeContext server not found locally**
A: The installer automatically falls back to the npm package. Ensure you have Node.js and npm installed, or build the local server.

**Q: Invalid JSON error when updating config**
A: The installer creates automatic backups and handles invalid JSON gracefully. Check the `.backup` file to recover previous configurations.

**Q: API key validation fails**
A: Ensure your VibeContext API key is valid and properly formatted. Keys should be alphanumeric with underscores/dashes only.

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Run installation with detailed logging
installer = MCPInstaller()
installer.install_mcp_servers("claude_code", Path.cwd(), api_key)
```

## Contributing

When contributing to the MCP installer:

1. **Add Tests**: Include unit tests for new functionality
2. **Update Documentation**: Keep this README current with changes
3. **Cross-Platform Testing**: Test on macOS, Linux, and Windows
4. **Error Handling**: Provide clear error messages for failure cases
5. **Backward Compatibility**: Maintain compatibility with existing configs

## License

This MCP installer service is part of the py_wizard_cli project and follows the same license terms.

---

For more information, see the example usage file and test suite for detailed implementation examples.