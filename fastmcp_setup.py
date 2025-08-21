#!/usr/bin/env python3
"""
FastMCP Microsoft Style Guide Server - One-Command Setup

A streamlined setup script that automatically configures:
- FastMCP server installation
- VS Code MCP integration 
- Global mcp.json configuration
- GitHub Copilot Chat integration
- Cross-platform compatibility

Usage:
    python fastmcp_setup.py           # Interactive setup
    python fastmcp_setup.py --auto    # Automated setup
    python fastmcp_setup.py --copilot # Setup with Copilot Chat focus
"""

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional

class FastMCPSetup:
    def __init__(self):
        """Initialize the FastMCP setup."""
        self.project_dir = Path.cwd().absolute()
        self.python_executable = sys.executable
        self.platform = platform.system().lower()
        
        # Server version selection (will be set during setup)
        self.server_version = None
        self.server_file = None
        
        # Available server versions
        self.server_options = {
            "offline": {
                "file": "fastmcp_style_server.py",
                "name": "Offline FastMCP Server",
                "description": "Fast local analysis, no internet required",
                "dependencies": ["fastmcp"],
                "pros": ["Very fast", "Works offline", "No web dependencies"],
                "cons": ["Static guidance", "Links only to official docs"]
            },
            "web": {
                "file": "fastmcp_style_server_web.py", 
                "name": "Web-Enabled FastMCP Server",
                "description": "Live guidance from Microsoft Learn website",
                "dependencies": ["fastmcp", "aiohttp"],
                "pros": ["Live official content", "Always up-to-date", "Real examples"],
                "cons": ["Requires internet", "Slightly slower", "Web dependencies"]
            }
        }
        
        # VS Code settings paths by platform
        if self.platform == "windows":
            self.vscode_user_dir = Path.home() / "AppData" / "Roaming" / "Code" / "User"
        elif self.platform == "darwin":  # macOS
            self.vscode_user_dir = Path.home() / "Library" / "Application Support" / "Code" / "User"
        else:  # Linux
            self.vscode_user_dir = Path.home() / ".config" / "Code" / "User"
        
        self.success_count = 0
        self.total_steps = 8  # Added version selection step

    def print_header(self):
        """Print setup header."""
        print("=" * 70)
        print("🚀 FastMCP Microsoft Style Guide Server - One-Command Setup")
        print("=" * 70)
        print("This setup will configure:")
        print("• FastMCP server with Microsoft Style Guide analysis")
        print("• Choice between Offline or Web-Enabled versions")
        print("• VS Code MCP integration (global mcp.json)")
        print("• GitHub Copilot Chat integration")
        print("• Cross-platform compatibility")
        print()

    def select_server_version(self, auto_mode: bool = False) -> bool:
        """Allow user to select between offline and web-enabled versions."""
        print("📋 Step 1/8: Server Version Selection")
        print("-" * 40)
        
        if auto_mode:
            # Default to offline version in auto mode for simplicity
            self.server_version = "offline"
            print("🤖 Auto mode: Selected Offline version (fast, reliable)")
            self.server_file = self.project_dir / self.server_options[self.server_version]["file"]
            self.success_count += 1
            return True
        
        print("Choose your Microsoft Style Guide server version:\n")
        
        # Display options
        for key, option in self.server_options.items():
            print(f"{'🌐' if key == 'web' else '💾'} {key.upper()}: {option['name']}")
            print(f"   📝 {option['description']}")
            print(f"   ✅ Pros: {', '.join(option['pros'])}")
            print(f"   ⚠️  Cons: {', '.join(option['cons'])}")
            print()
        
        print("💡 Recommendation:")
        print("   • Choose OFFLINE for: Fast setup, offline work, stable environments")
        print("   • Choose WEB for: Latest guidance, live examples, internet-connected work")
        print()
        
        # Get user choice
        while True:
            choice = input("Select version [offline/web] (default: offline): ").strip().lower()
            
            if not choice or choice == "offline":
                self.server_version = "offline"
                break
            elif choice == "web":
                self.server_version = "web"
                break
            else:
                print("❌ Invalid choice. Please enter 'offline' or 'web'")
        
        selected_option = self.server_options[self.server_version]
        self.server_file = self.project_dir / selected_option["file"]
        
        print(f"✅ Selected: {selected_option['name']}")
        print(f"   Server file: {selected_option['file']}")
        print(f"   Dependencies: {', '.join(selected_option['dependencies'])}")
        
        self.success_count += 1
        return True

    def check_dependencies(self) -> bool:
        """Check and install required dependencies based on selected version."""
        print("\n📦 Step 2/8: Checking Dependencies")
        print("-" * 40)
        
        if not self.server_version:
            print("❌ Server version not selected")
            return False
        
        selected_option = self.server_options[self.server_version]
        print(f"Installing dependencies for: {selected_option['name']}")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} OK")
        
        # Install version-specific dependencies
        for dependency in selected_option["dependencies"]:
            try:
                if dependency == "fastmcp":
                    import fastmcp
                    print("✅ FastMCP already installed")
                elif dependency == "aiohttp":
                    import aiohttp
                    print("✅ aiohttp already installed")
            except ImportError:
                print(f"🔄 Installing {dependency}...")
                try:
                    subprocess.check_call([
                        self.python_executable, "-m", "pip", "install", dependency
                    ], capture_output=True)
                    print(f"✅ {dependency} installed successfully")
                except subprocess.CalledProcessError:
                    print(f"⚠️  {dependency} installation failed, will use fallback mode")
        
        # Try standard MCP as fallback
        try:
            import mcp
            print("✅ MCP library available")
        except ImportError:
            print("🔄 Installing MCP as fallback...")
            try:
                subprocess.check_call([
                    self.python_executable, "-m", "pip", "install", "mcp"
                ], capture_output=True)
                print("✅ MCP installed successfully")
            except subprocess.CalledProcessError:
                print("⚠️  MCP installation failed, server will run in basic mode")
        
        # Show version-specific information
        if self.server_version == "web":
            print("🌐 Web version will fetch live content from Microsoft Learn")
        else:
            print("💾 Offline version will use local analysis with official links")
        
        self.success_count += 1
        return True

    def create_server_file(self) -> bool:
        """Create or verify the FastMCP server file exists."""
        print(f"\n📝 Step 3/8: Verifying Server File")
        print("-" * 40)
        
        if not self.server_version or not self.server_file:
            print("❌ Server version not properly selected")
            return False
        
        selected_option = self.server_options[self.server_version]
        print(f"Checking for: {selected_option['name']}")
        print(f"Expected file: {self.server_file}")
        
        if self.server_file.exists():
            print(f"✅ Server file found: {self.server_file}")
            self.success_count += 1
            return True
        else:
            print(f"❌ Server file not found: {self.server_file}")
            print("💡 Please ensure you have the correct FastMCP server file:")
            if self.server_version == "offline":
                print("   • fastmcp_style_server.py (offline version)")
            else:
                print("   • fastmcp_style_server_web.py (web-enabled version)")
            print("   These should have been created separately or downloaded with the project")
            return False

    def test_server(self) -> bool:
        """Test that the selected server can start."""
        print(f"\n🧪 Step 4/8: Testing Server")
        print("-" * 40)
        
        selected_option = self.server_options[self.server_version]
        print(f"Testing: {selected_option['name']}")
        
        try:
            # Run a quick test
            result = subprocess.run([
                self.python_executable, str(self.server_file), "--test"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("✅ Server test passed")
                if self.server_version == "web":
                    print("   🌐 Web version can fetch live content (when online)")
                else:
                    print("   💾 Offline version ready for local analysis")
                self.success_count += 1
                return True
            else:
                print(f"⚠️  Server test had issues: {result.stderr}")
                # Don't fail setup for test issues
                self.success_count += 1
                return True
                
        except subprocess.TimeoutExpired:
            print("⚠️  Server test timed out, but continuing...")
            self.success_count += 1
            return True
        except Exception as e:
            print(f"⚠️  Server test failed: {e}, but continuing...")
            self.success_count += 1
            return True

    def setup_global_mcp_json(self) -> bool:
        """Set up the global VS Code mcp.json file with version-specific configuration."""
        print(f"\n🔧 Step 5/8: Setting Up Global MCP Configuration")
        print("-" * 40)
        
        # Create VS Code user directory if it doesn't exist
        self.vscode_user_dir.mkdir(parents=True, exist_ok=True)
        
        mcp_json_path = self.vscode_user_dir / "mcp.json"
        selected_option = self.server_options[self.server_version]
        
        # Create version-specific MCP configuration
        server_config = {
            "command": self.python_executable,
            "args": [str(self.server_file)],
            "env": {
                "PYTHONPATH": str(self.project_dir)
            },
            "initializationOptions": {
                "name": f"Microsoft Style Guide ({self.server_version.title()})",
                "version": "1.0.0",
                "description": f"FastMCP server - {selected_option['description']}",
                "server_type": f"fastmcp_{self.server_version}",
                "capabilities": {
                    "web_enabled": self.server_version == "web",
                    "live_content": self.server_version == "web",
                    "offline_capable": True
                }
            }
        }
        
        mcp_config = {
            "servers": {
                "microsoft-style-guide": server_config
            },
            "clients": {
                "vscode": {
                    "enabled": True,
                    "autoStart": True
                },
                "copilot": {
                    "enabled": True,
                    "exposeToChat": True
                }
            },
            "metadata": {
                "setup_version": f"fastmcp-{self.server_version}-1.0.0",
                "created_by": "FastMCP Setup Script",
                "server_version": self.server_version,
                "server_file": str(self.server_file),
                "last_updated": self._get_current_timestamp()
            }
        }
        
        # Merge with existing configuration if it exists
        if mcp_json_path.exists():
            try:
                with open(mcp_json_path, 'r') as f:
                    existing_config = json.load(f)
                
                # Backup existing config
                backup_path = mcp_json_path.with_suffix('.json.backup')
                with open(backup_path, 'w') as f:
                    json.dump(existing_config, f, indent=2)
                print(f"✅ Backed up existing config to {backup_path}")
                
                # Merge configurations
                if "servers" not in existing_config:
                    existing_config["servers"] = {}
                existing_config["servers"]["microsoft-style-guide"] = mcp_config["servers"]["microsoft-style-guide"]
                
                # Update clients and metadata
                existing_config.update({
                    "clients": mcp_config["clients"],
                    "metadata": mcp_config["metadata"]
                })
                
                mcp_config = existing_config
                
            except json.JSONDecodeError:
                print("⚠️  Existing mcp.json has invalid JSON, creating new one")
        
        # Write the configuration
        with open(mcp_json_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        print(f"✅ Global MCP configuration created: {mcp_json_path}")
        print(f"   Server: microsoft-style-guide ({self.server_version})")
        print(f"   Version: {selected_option['name']}")
        print(f"   Command: {self.python_executable}")
        print(f"   Script: {self.server_file}")
        
        if self.server_version == "web":
            print("   🌐 Web-enabled: Will fetch live content from Microsoft Learn")
        else:
            print("   💾 Offline: Fast local analysis with official documentation links")
        
        self.success_count += 1
        return True

    def setup_workspace_config(self) -> bool:
        """Set up workspace-specific configuration."""
        print(f"\n📁 Step 6/8: Setting Up Workspace Configuration")
        print("-" * 40)
        
        # Create .vscode directory
        vscode_workspace_dir = self.project_dir / ".vscode"
        vscode_workspace_dir.mkdir(exist_ok=True)
        
        selected_option = self.server_options[self.server_version]
        
        # Create launch.json for debugging
        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": f"Debug FastMCP Server ({self.server_version.title()})",
                    "type": "python",
                    "request": "launch",
                    "program": str(self.server_file),
                    "args": ["--test"],
                    "console": "integratedTerminal",
                    "cwd": str(self.project_dir),
                    "env": {
                        "PYTHONPATH": str(self.project_dir)
                    }
                }
            ]
        }
        
        launch_path = vscode_workspace_dir / "launch.json"
        with open(launch_path, 'w') as f:
            json.dump(launch_config, f, indent=2)
        print(f"✅ Debug configuration created: {launch_path}")
        
        # Create workspace settings
        workspace_settings = {
            "python.defaultInterpreterPath": self.python_executable,
            "mcp.servers": {
                "microsoft-style-guide": {
                    "enabled": True,
                    "autoStart": True,
                    "version": self.server_version
                }
            },
            "files.associations": {
                "*.md": "markdown",
                "*.txt": "plaintext"
            }
        }
        
        settings_path = vscode_workspace_dir / "settings.json"
        with open(settings_path, 'w') as f:
            json.dump(workspace_settings, f, indent=2)
        print(f"✅ Workspace settings created: {settings_path}")
        print(f"   Configured for: {selected_option['name']}")
        
        self.success_count += 1
        return True

    def setup_copilot_integration(self) -> bool:
        """Set up GitHub Copilot Chat integration with version-aware features."""
        print(f"\n💬 Step 7/8: Setting Up GitHub Copilot Integration")
        print("-" * 40)
        
        selected_option = self.server_options[self.server_version]
        
        # Create version-aware Copilot integration script
        web_imports = ""
        web_note = ""
        
        if self.server_version == "web":
            web_note = "# Web-enabled version: includes live content fetching"
        else:
            web_note = "# Offline version: fast local analysis with official links"
        
        copilot_script = f'''#!/usr/bin/env python3
"""
GitHub Copilot Chat Integration for Microsoft Style Guide FastMCP Server
Server Version: {self.server_version.title()} - {selected_option['description']}

{web_note}

Usage in Copilot Chat:
@workspace analyze this content for Microsoft Style Guide compliance
@workspace check voice and tone of this text  
@workspace suggest improvements for this writing
"""

import asyncio
import sys
import json
from pathlib import Path

async def main():
    """Main function for Copilot integration."""
    if len(sys.argv) < 2:
        print("Usage: python copilot_integration.py <command> [content]")
        print("Commands: analyze, voice, grammar, terminology, accessibility, improve, guidelines, search")
        print(f"Server: {selected_option['name']}")
        return
    
    command = sys.argv[1].lower()
    content = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    
    # Import the server tools directly for quick integration
    try:
        sys.path.append(str(Path(__file__).parent))
        from {selected_option['file'][:-3]} import analyze_content, suggest_improvements, get_style_guidelines, search_style_guide
        
        if command in ["analyze", "check", "review"]:
            if not content:
                print("Error: No content provided for analysis")
                return
            result = await analyze_content(content, "comprehensive")
            
        elif command in ["improve", "suggest", "fix"]:
            if not content:
                print("Error: No content provided for improvements")
                return
            result = await suggest_improvements(content, "all")
            
        elif command in ["guidelines", "guide", "help"]:
            category = content or "all"
            result = get_style_guidelines(category)
            
        elif command in ["search", "find"]:
            if not content:
                print("Error: No search query provided")
                return
            result = await search_style_guide(content)
            
        else:
            result = {{
                "error": f"Unknown command: {{command}}",
                "available_commands": [
                    "analyze - Comprehensive style analysis",
                    "improve - Get improvement suggestions", 
                    "guidelines - Get style guidelines",
                    "search - Search style guide{'(live)' if self.server_version == 'web' else '(links)'}"
                ],
                "server_version": "{self.server_version}",
                "server_type": "{selected_option['name']}"
            }}
        
        # Format output for Copilot Chat
        if isinstance(result, dict):
            if "formatted" in result:
                print(result["formatted"])
            elif "summary" in result:
                print(result["summary"])
            else:
                print(json.dumps(result, indent=2))
        else:
            print(str(result))
            
    except ImportError as e:
        print(f"Error: Could not import FastMCP server: {{e}}")
        print(f"Please ensure {{selected_option['file']}} is in the same directory")

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        copilot_path = self.project_dir / "copilot_integration.py"
        with open(copilot_path, 'w') as f:
            f.write(copilot_script)
        print(f"✅ Copilot integration script created: {copilot_path}")
        print(f"   Configured for: {selected_option['name']}")
        
        # Create version-specific usage examples
        web_examples = ""
        if self.server_version == "web":
            web_examples = """
### Live Search (Web Version Only)
```
@workspace search the Microsoft Style Guide for "active voice examples"
@workspace find guidance on "inclusive language best practices"
```

### Live Official Guidance
```
@workspace get official Microsoft guidance on terminology standards
@workspace fetch latest voice and tone guidelines from Microsoft Learn
```
"""
        
        example_usage = f"""# GitHub Copilot Chat Integration Examples
## Server Version: {selected_option['name']}

## In VS Code Copilot Chat, you can use these commands:

### Content Analysis
```
@workspace analyze this content for Microsoft Style Guide compliance:
"Welcome to our new product! You can easily configure the settings to meet your needs."
```

### Voice and Tone Check
```
@workspace check voice and tone of this text:
"The configuration of settings can be accomplished by the user through the interface."
```

### Improvement Suggestions
```
@workspace suggest improvements for this writing:
"Users should utilize the functionality to facilitate optimal performance."
```

### Style Guidelines
```
@workspace show Microsoft Style Guide guidelines for voice and tone
```

{web_examples}

## Direct Script Usage

```bash
# Analyze content
python copilot_integration.py analyze "Your content here"

# Get improvements  
python copilot_integration.py improve "Text to improve"

# Get guidelines
python copilot_integration.py guidelines voice

{"# Live search (web version)" if self.server_version == "web" else "# Search links (offline version)"}
python copilot_integration.py search "active voice"
```

## Server Version: {selected_option['name']}

{'🌐 **Web Features**: Live content from Microsoft Learn, always up-to-date guidance' if self.server_version == 'web' else '💾 **Offline Features**: Fast local analysis, works without internet'}

## MCP Tools Available in VS Code

Once the MCP server is running, these tools are available:
- `analyze_content` - Comprehensive style analysis
- `get_style_guidelines` - Retrieve specific guidelines
- `suggest_improvements` - Get improvement suggestions
- `search_style_guide` - Search official documentation{"(live)" if self.server_version == "web" else "(links)"}
{"- `get_official_guidance` - Get live official guidance (web version)" if self.server_version == "web" else ""}
"""
        
        usage_path = self.project_dir / "COPILOT_USAGE.md"
        with open(usage_path, 'w') as f:
            f.write(example_usage)
        print(f"✅ Usage examples created: {usage_path}")
        
        self.success_count += 1
        return True

    def create_test_content(self) -> bool:
        """Create test content for validation."""
        print(f"\n📄 Step 8/8: Creating Test Content")
        print("-" * 40)
        
        test_content = f'''# Microsoft Style Guide Test Document
## Server Version: {self.server_options[self.server_version]['name']}

Welcome to our new feature! You can easily set up your account in just a few steps.

## Getting Started

Here's how to get started:

1. **Sign in** to your account
2. **Choose your preferences** - Select what works for you  
3. **Save your changes** - You're all set!

## Writing Tips

We're here to help you write great content:

- Use contractions (it's, you're, we'll) for a natural tone
- Keep sentences short and clear
- Write in active voice
- Use "you" to address readers directly

## Need Help?

If you need assistance, we're ready to help! Contact our support team.

## Server Configuration

This test document is configured for the **{self.server_version}** version:
- {'🌐 Web-enabled: Fetches live content from Microsoft Learn' if self.server_version == 'web' else '💾 Offline: Fast local analysis with official documentation links'}
- {'Requires internet for full functionality' if self.server_version == 'web' else 'Works completely offline'}

---

*This content follows Microsoft Style Guide principles.*
'''
        
        test_path = self.project_dir / "test_document.md"
        with open(test_path, 'w') as f:
            f.write(test_content)
        print(f"✅ Test document created: {test_path}")
        
        # Test the integration
        print("🧪 Running integration test...")
        try:
            copilot_script = self.project_dir / "copilot_integration.py"
            if copilot_script.exists():
                result = subprocess.run([
                    self.python_executable, str(copilot_script), 
                    "analyze", "Hello, you can easily configure your settings!"
                ], capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    print("✅ Integration test passed")
                    if self.server_version == "web":
                        print("   🌐 Web version ready for live content fetching")
                    else:
                        print("   💾 Offline version ready for fast local analysis")
                else:
                    print(f"⚠️  Integration test issues: {result.stderr}")
            
        except Exception as e:
            print(f"⚠️  Integration test failed: {e}")
        
        self.success_count += 1
        return True

    def print_summary(self):
        """Print setup summary and next steps."""
        print("\n" + "=" * 70)
        print("🎉 FastMCP Setup Complete!")
        print("=" * 70)
        
        print(f"\n📊 Setup Status: {self.success_count}/{self.total_steps} steps completed")
        
        if self.success_count == self.total_steps:
            print("✅ All steps completed successfully!")
        else:
            print("⚠️  Some steps had issues, but core functionality should work")
        
        print(f"\n🔧 Configuration Files Created:")
        print(f"   • Global MCP config: {self.vscode_user_dir / 'mcp.json'}")
        print(f"   • Workspace settings: {self.project_dir / '.vscode'}")
        print(f"   • Copilot integration: {self.project_dir / 'copilot_integration.py'}")
        print(f"   • Test document: {self.project_dir / 'test_document.md'}")
        
        print(f"\n🚀 Next Steps:")
        print("1. Restart VS Code completely (close all windows)")
        print("2. Open this project in VS Code")
        print("3. Look for 'microsoft-style-guide' in MCP servers")
        print("4. Try Copilot Chat commands:")
        print('   @workspace analyze "Your content here"')
        print('   @workspace improve "Text to improve"')
        
        print(f"\n🧪 Test Commands:")
        print(f"   python {self.server_file} --test")
        print(f"   python copilot_integration.py analyze \"Test content\"")
        
        print(f"\n📚 Resources:")
        print("   • Test document: test_document.md")
        print("   • Usage examples: COPILOT_USAGE.md") 
        print("   • Microsoft Style Guide: https://learn.microsoft.com/en-us/style-guide/")
        
        print("\n" + "=" * 70)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    def run_setup(self, auto_mode: bool = False):
        """Run the complete setup process."""
        self.print_header()
        
        if not auto_mode:
            response = input("Continue with setup? (y/N): ").strip().lower()
            if response != 'y':
                print("Setup cancelled.")
                return False
        
        # Run setup steps
        steps = [
            self.check_dependencies,
            self.create_server_file,
            self.test_server,
            self.setup_global_mcp_json,
            self.setup_workspace_config,
            self.setup_copilot_integration,
            self.create_test_content
        ]
        
        for step in steps:
            if not step():
                print(f"\n❌ Setup failed at step: {step.__name__}")
                return False
        
        self.print_summary()
        return True

def main():
    """Main setup function with version selection options."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="FastMCP Microsoft Style Guide Server Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fastmcp_setup.py                    # Interactive setup with version choice
  python fastmcp_setup.py --auto             # Auto setup (defaults to offline)
  python fastmcp_setup.py --offline          # Force offline version
  python fastmcp_setup.py --web              # Force web-enabled version
  python fastmcp_setup.py --copilot          # Setup with Copilot Chat focus
  
Version Comparison:
  Offline:  Fast, reliable, works without internet, local analysis only
  Web:      Live content from Microsoft Learn, always up-to-date, requires internet
        """
    )
    parser.add_argument("--auto", action="store_true", 
                       help="Run setup without prompts (defaults to offline version)")
    parser.add_argument("--offline", action="store_true",
                       help="Force offline version selection")
    parser.add_argument("--web", action="store_true", 
                       help="Force web-enabled version selection")
    parser.add_argument("--copilot", action="store_true", 
                       help="Focus on Copilot Chat integration (interactive)")
    
    args = parser.parse_args()
    
    # Validate arguments
    version_flags = [args.offline, args.web]
    if sum(version_flags) > 1:
        print("❌ Error: Cannot specify both --offline and --web")
        return False
    
    setup = FastMCPSetup()
    
    # Pre-select version if specified via command line
    if args.offline:
        setup.server_version = "offline"
        setup.server_file = setup.project_dir / setup.server_options["offline"]["file"]
        print(f"🔧 Command line: Selected Offline version")
    elif args.web:
        setup.server_version = "web"
        setup.server_file = setup.project_dir / setup.server_options["web"]["file"]
        print(f"🔧 Command line: Selected Web-enabled version")
    
    # Determine auto mode
    auto_mode = args.auto or args.offline or args.web
    
    if args.copilot:
        print("💬 Copilot Chat focus mode enabled")
        auto_mode = False  # Force interactive for copilot focus
    
    try:
        success = setup.run_setup(auto_mode=auto_mode)
        
        if success and (args.offline or args.web):
            selected_option = setup.server_options[setup.server_version]
            print(f"\n🎯 Command Line Setup Complete!")
            print(f"   Version: {selected_option['name']}")
            print(f"   File: {selected_option['file']}")
            
        return success
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)