# Microsoft Style Guide MCP Server Updater

This document explains how to use the MCP server updater script to keep your Microsoft Style Guide MCP server up to date.

## Features

- Automatically checks for updates from the GitHub repository
- Supports both GitHub releases and latest commits from main branch
- Creates automatic backups before updating
- Can restore from backups if updates fail
- Configuration via JSON file

## Usage

### Check for Updates

```bash
python mcp_updater.py check
```

This checks if updates are available and displays version information.

### Perform Update

```bash
python mcp_updater.py update
```

This downloads and applies updates if available. The system creates a backup automatically.

### Force Update

```bash
python mcp_updater.py update --force
```

This forces an update even if the system detects no new version.

### Show Status

```bash
python mcp_updater.py status
```

Displays current version information and configuration.

### Restore from Backup

```bash
python mcp_updater.py restore --backup-path backups/backup_20241201_143022
```

Restores files from a specific backup directory.

## Configuration

The updater reads configuration from `update_config.json`:

```json
{
  "repository": {
    "owner": "asudbring",
    "name": "ms-style-guide-fastmcp-server",
    "branch": "main"
  },
  "update_settings": {
    "auto_update": false,
    "backup_retention_days": 30,
    "check_interval_hours": 24
  }
}
```

## Files Updated

The updater updates these files during an update:

- `fastmcp_style_server.py` - Main MCP server implementation
- `fastmcp_style_server_web.py` - Web-enabled MCP server
- `copilot_integration.py` - Copilot integration features
- `requirements.txt` - Python dependencies
- `fastmcp_setup.py` - Setup script
- `readme.md` - Documentation

## Files Preserved

These files are preserved during updates:

- `.vscode/settings.json` - VS Code configuration
- `vscode_mcp_config.json` - MCP configuration
- `mcp_manifest.json` - Manifest file
- `test_document.md` - Test documents
- `copilot_integration.py` - Integration scripts

## Backup System

- Backups are created in the `backups/` directory
- Each backup is timestamped: `backup_YYYYMMDD_HHMMSS`
- Backup metadata is stored in `backup_info.json`
- Failed updates automatically restore from the most recent backup

## Version Detection

The updater detects the current version using:

1. `.mcp_version` file (if exists)
2. Git tags (if on a tagged commit)
3. Git commit hash (short form)
4. Default fallback version

## Requirements

- Python 3.8+
- `aiohttp` library (for HTTP requests)
- Git (for version detection)
- Internet connection (for GitHub API access)

## Troubleshooting

### Error: GitHub API error: 404

This usually means:
- The repository doesn't have any releases yet (normal, will use latest commit)
- Network connectivity issues
- Repository access permissions

### Error: HTTP session not available

This means `aiohttp` isn't installed. Install it with:

```bash
pip install aiohttp
```

### Update fails during file extraction

The updater automatically restores from backup. Check the error message and ensure:
- You have write permissions to the directory
- No files are currently in use by other processes
- Sufficient disk space is available

## Command Line Options

```
python mcp_updater.py <action> [options]

Actions:
  check           Check for updates
  update          Update if available
  status          Show status information
  restore         Restore from backup

Options:
  --force         Force update even if no new version detected
  --repo-owner    GitHub repository owner (default: asudbring)
  --repo-name     GitHub repository name (default: ms-style-guide-fastmcp-server)
  --backup-path   Backup path for restore action
```

## Integration with VS Code

After an update, you may need to:

1. Restart VS Code
2. Restart the MCP server
3. Reload any MCP configurations

The updater notifies you when you need to restart.
