#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Microsoft Style Guide MCP Client - FastMCP Compatible

This client connects to the Microsoft Style Guide FastMCP Server and provides
interfaces for VSCode, GitHub Copilot Chat, and command-line usage.

Cross-platform compatible: Windows, macOS, Linux
"""

import asyncio
import json
import logging
import sys
import argparse
import os
import platform
import subprocess
from typing import Any, Dict, List, Optional
from pathlib import Path

# Cross-platform encoding setup
def setup_encoding():
    """Setup proper encoding for cross-platform compatibility."""
    if sys.platform == "win32":
        try:
            # Try to set console code page to UTF-8 on Windows
            os.system("chcp 65001 > nul 2>&1")
        except:
            pass
    
    # Ensure stdout/stderr can handle Unicode
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

setup_encoding()

# Configure logging with cross-platform support
def setup_logging():
    """Setup cross-platform logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory if it doesn't exist
    log_dir = Path.home() / ".microsoft-style-guide-mcp" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "mcp_client.log", encoding='utf-8')
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

# Safe print function for Unicode characters across platforms
def safe_print(text):
    """Print text safely, handling Unicode encoding issues across platforms."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback to ASCII-safe version
        safe_text = text.encode('ascii', errors='replace').decode('ascii')
        print(safe_text)

# HTTP client for direct server communication (fallback)
try:
    import httpx
    HTTP_CLIENT = "httpx"
except ImportError:
    try:
        import aiohttp
        HTTP_CLIENT = "aiohttp"
    except ImportError:
        HTTP_CLIENT = None

# Try to import MCP clients with fallbacks
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.types import CallToolRequest, ListToolsRequest
    MCP_AVAILABLE = True
    logger.info("MCP library detected - using standard MCP client")
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP library not available - using HTTP fallback")

class FastMCPClient:
    """Client for FastMCP servers with cross-platform support."""
    
    def __init__(self):
        """Initialize the FastMCP client."""
        self.session: Optional[Any] = None
        self.available_tools: List[str] = []
        self.server_process = None
        self.server_url = None
        self.connection_type = None
        self.platform_info = self.get_platform_info()
    
    def get_platform_info(self) -> Dict[str, str]:
        """Get cross-platform system information."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "mcp_available": MCP_AVAILABLE,
            "http_client": HTTP_CLIENT or "none"
        }
    
    async def connect_stdio(self, server_script_path: str) -> bool:
        """Connect via stdio (traditional MCP)."""
        try:
            if not MCP_AVAILABLE:
                logger.error("MCP library not available for stdio connection")
                return False
            
            # Prepare server parameters
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[server_script_path]
            )
            
            # Connect using stdio
            stdio_transport = await stdio_client(server_params)
            self.session = ClientSession(stdio_transport[0], stdio_transport[1])
            
            # Initialize the session
            init_result = await self.session.initialize()
            logger.info(f"Connected to FastMCP server via stdio")
            logger.debug(f"Server info: {init_result}")
            
            # List available tools
            tools_result = await self.session.list_tools(ListToolsRequest())
            self.available_tools = [tool.name for tool in tools_result.tools]
            logger.info(f"Available tools: {', '.join(self.available_tools)}")
            
            self.connection_type = "stdio"
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect via stdio: {e}")
            return False
    
    async def connect_http(self, server_url: str = None) -> bool:
        """Connect via HTTP (FastMCP server)."""
        try:
            if not HTTP_CLIENT:
                logger.error("No HTTP client available for HTTP connection")
                return False
            
            # Default server URL
            if not server_url:
                server_url = "http://localhost:3000"
            
            self.server_url = server_url
            
            # Create HTTP session
            if HTTP_CLIENT == "httpx":
                self.session = httpx.AsyncClient(timeout=30.0)
            else:  # aiohttp
                timeout = aiohttp.ClientTimeout(total=30)
                self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Test connection and get available tools
            health_url = f"{server_url}/health"
            tools_url = f"{server_url}/tools"
            
            if HTTP_CLIENT == "httpx":
                # Test connection
                response = await self.session.get(health_url)
                if response.status_code != 200:
                    raise Exception(f"Server health check failed: {response.status_code}")
                
                # Get tools
                response = await self.session.get(tools_url)
                if response.status_code == 200:
                    tools_data = response.json()
                    self.available_tools = [tool["name"] for tool in tools_data.get("tools", [])]
            else:  # aiohttp
                # Test connection
                async with self.session.get(health_url) as response:
                    if response.status != 200:
                        raise Exception(f"Server health check failed: {response.status}")
                
                # Get tools
                async with self.session.get(tools_url) as response:
                    if response.status == 200:
                        tools_data = await response.json()
                        self.available_tools = [tool["name"] for tool in tools_data.get("tools", [])]
            
            logger.info(f"Connected to FastMCP server via HTTP at {server_url}")
            logger.info(f"Available tools: {', '.join(self.available_tools)}")
            
            self.connection_type = "http"
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect via HTTP: {e}")
            return False
    
    async def connect(self, server_script_path: str = None, server_url: str = None) -> bool:
        """Connect to FastMCP server (try multiple methods)."""
        # Try stdio connection first if script path provided
        if server_script_path and Path(server_script_path).exists():
            if await self.connect_stdio(server_script_path):
                return True
            logger.warning("Stdio connection failed, trying HTTP...")
        
        # Try HTTP connection
        if await self.connect_http(server_url):
            return True
        
        # If both fail, try starting the server ourselves
        if server_script_path and Path(server_script_path).exists():
            return await self.start_and_connect_server(server_script_path)
        
        return False
    
    async def start_and_connect_server(self, server_script_path: str) -> bool:
        """Start the server process and connect to it."""
        try:
            logger.info("Attempting to start FastMCP server...")
            
            # Start the server process
            self.server_process = subprocess.Popen(
                [sys.executable, server_script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path(server_script_path).parent
            )
            
            # Give the server time to start
            await asyncio.sleep(2)
            
            # Check if process is still running
            if self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                logger.error(f"Server failed to start. Stdout: {stdout}, Stderr: {stderr}")
                return False
            
            # Try to connect via HTTP
            if await self.connect_http():
                logger.info("Successfully started and connected to FastMCP server")
                return True
            
            # If HTTP fails, try stdio
            self.terminate_server()
            return await self.connect_stdio(server_script_path)
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            self.terminate_server()
            return False
    
    def terminate_server(self):
        """Terminate the server process if we started it."""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
            except Exception as e:
                logger.error(f"Error terminating server: {e}")
            finally:
                self.server_process = None
    
    async def disconnect(self):
        """Disconnect from the FastMCP server."""
        if self.session:
            try:
                if self.connection_type == "http":
                    if HTTP_CLIENT == "httpx":
                        await self.session.aclose()
                    else:  # aiohttp
                        await self.session.close()
                elif self.connection_type == "stdio":
                    await self.session.close()
                logger.info("Disconnected from FastMCP server")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.session = None
        
        self.terminate_server()
    
    def _handle_response(self, result) -> Dict[str, Any]:
        """Handle response from server (both MCP and HTTP)."""
        try:
            if self.connection_type == "stdio":
                # Standard MCP response
                if hasattr(result, 'content') and result.content:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        return {"success": True, "result": content.text}
                    else:
                        return {"success": True, "result": str(content)}
                else:
                    return {"success": True, "result": str(result)}
            
            elif self.connection_type == "http":
                # HTTP response (should be JSON)
                if isinstance(result, dict):
                    return {"success": True, "result": result}
                else:
                    return {"success": True, "result": str(result)}
            
            return {"success": True, "result": str(result)}
            
        except Exception as e:
            return {"success": False, "error": f"Error processing response: {e}"}
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the FastMCP server."""
        if not self.session:
            return {"success": False, "error": "Not connected to server"}
        
        try:
            if self.connection_type == "stdio":
                # Standard MCP call
                result = await self.session.call_tool(
                    CallToolRequest(
                        name=tool_name,
                        arguments=arguments
                    )
                )
                return self._handle_response(result)
            
            elif self.connection_type == "http":
                # HTTP call to FastMCP server
                url = f"{self.server_url}/tools/{tool_name}"
                payload = {"arguments": arguments}
                
                if HTTP_CLIENT == "httpx":
                    response = await self.session.post(url, json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        return {"success": True, "result": result}
                    else:
                        return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                else:  # aiohttp
                    async with self.session.post(url, json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            return {"success": True, "result": result}
                        else:
                            error_text = await response.text()
                            return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
            
            return {"success": False, "error": "Unknown connection type"}
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_content(self, text: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze content using the Microsoft Style Guide."""
        return await self.call_tool("analyze_content", {
            "text": text,
            "analysis_type": analysis_type
        })
    
    async def get_style_guidelines(self, category: str = "all") -> Dict[str, Any]:
        """Get Microsoft Style Guide guidelines."""
        return await self.call_tool("get_style_guidelines", {
            "category": category
        })
    
    async def suggest_improvements(self, text: str, focus_area: str = "all") -> Dict[str, Any]:
        """Get improvement suggestions for content."""
        return await self.call_tool("suggest_improvements", {
            "text": text,
            "focus_area": focus_area
        })

    async def search_style_guide(self, query: str) -> Dict[str, Any]:
        """Search the Microsoft Style Guide website (web-enabled version only)."""
        return await self.call_tool("search_style_guide", {
            "query": query
        })
    
    async def get_official_guidance(self, issue_type: str, specific_term: str = "") -> Dict[str, Any]:
        """Get official guidance for specific issues (web-enabled version only)."""
        return await self.call_tool("get_official_guidance", {
            "issue_type": issue_type,
            "specific_term": specific_term
        })
    
    async def check_terminology(self, terms: List[str]) -> Dict[str, Any]:
        """Check terminology against Microsoft standards."""
        return await self.call_tool("check_terminology", {
            "terms": terms
        })

class VSCodeInterface:
    """Interface for VSCode integration via GitHub Copilot Chat."""
    
    def __init__(self, client: FastMCPClient):
        """Initialize VSCode interface."""
        self.client = client
    
    async def analyze_file(self, file_path: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze a file for Microsoft Style Guide compliance."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            # Read file with proper encoding detection
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path_obj, 'r', encoding=encoding) as file:
                        content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                return {"success": False, "error": f"Could not decode file: {file_path}"}
            
            if not content.strip():
                return {"success": False, "error": "File is empty"}
            
            result = await self.client.analyze_content(content, analysis_type)
            if result["success"]:
                result["file_path"] = str(file_path)
                result["file_size"] = len(content)
                result["platform"] = self.client.platform_info["system"]
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_selection(self, text: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze selected text for Microsoft Style Guide compliance."""
        if not text.strip():
            return {"success": False, "error": "No text selected"}
        
        return await self.client.analyze_content(text, analysis_type)
    
    async def get_quick_fixes(self, text: str) -> Dict[str, Any]:
        """Get quick fix suggestions for text."""
        return await self.client.suggest_improvements(text, "all")

class GitHubCopilotInterface:
    """Interface for GitHub Copilot Chat integration."""
    
    def __init__(self, client: FastMCPClient):
        """Initialize GitHub Copilot interface."""
        self.client = client
    
    async def process_chat_command(self, command: str, content: str = "") -> Dict[str, Any]:
        """Process GitHub Copilot chat commands for Microsoft Style Guide."""
        command = command.lower().strip()
        
        # Handle different command patterns
        if command in ["analyze", "check", "review", "style-check"]:
            if not content:
                return {"success": False, "error": "No content provided for analysis"}
            return await self.client.analyze_content(content, "comprehensive")
        
        elif command in ["voice", "tone", "voice-tone"]:
            if not content:
                return {"success": False, "error": "No content provided for voice analysis"}
            return await self.client.analyze_content(content, "voice_tone")
        
        elif command in ["grammar", "style", "writing"]:
            if not content:
                return {"success": False, "error": "No content provided for grammar analysis"}
            return await self.client.analyze_content(content, "grammar")
        
        elif command in ["terms", "terminology", "vocab"]:
            if not content:
                return {"success": False, "error": "No content provided for terminology analysis"}
            return await self.client.analyze_content(content, "terminology")
        
        elif command in ["accessibility", "inclusive", "bias"]:
            if not content:
                return {"success": False, "error": "No content provided for accessibility analysis"}
            return await self.client.analyze_content(content, "accessibility")
        
        elif command in ["improve", "suggest", "fix", "help"]:
            if not content:
                return {"success": False, "error": "No content provided for improvement suggestions"}
            return await self.client.suggest_improvements(content, "all")
        
        elif command in ["guidelines", "rules", "guide"]:
            return await self.client.get_style_guidelines("all")
        
        elif command.startswith("guidelines-"):
            category = command.replace("guidelines-", "")
            if category in ["voice", "grammar", "terminology", "accessibility"]:
                return await self.client.get_style_guidelines(category)
            else:
                return {"success": False, "error": f"Unknown guidelines category: {category}"}
        
        elif command in ["search"]:
            if not content:
                return {"success": False, "error": "No search query provided"}
            return await self.client.search_style_guide(content)
        
        else:
            return {
                "success": False,
                "error": f"Unknown command: {command}",
                "available_commands": [
                    "analyze - Comprehensive style analysis",
                    "voice - Voice and tone analysis",
                    "grammar - Grammar and style analysis",
                    "terminology - Terminology consistency",
                    "accessibility - Inclusive language check",
                    "improve - Get improvement suggestions",
                    "guidelines - Get style guidelines",
                    "search - Search style guide (web version only)",
                    "guidelines-voice - Voice guidelines only",
                    "guidelines-grammar - Grammar guidelines only",
                    "guidelines-terminology - Terminology guidelines only",
                    "guidelines-accessibility - Accessibility guidelines only"
                ]
            }
    
    async def analyze_file_from_chat(self, file_path: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze a file mentioned in chat."""
        vscode_interface = VSCodeInterface(self.client)
        return await vscode_interface.analyze_file(file_path, analysis_type)

class CLIInterface:
    """Command-line interface for the client."""
    
    def __init__(self, client: FastMCPClient):
        """Initialize CLI interface."""
        self.client = client
        self.vscode = VSCodeInterface(client)
        self.copilot = GitHubCopilotInterface(client)
    
    async def run_interactive(self):
        """Run interactive mode for command-line usage."""
        safe_print("🎯 Microsoft Style Guide FastMCP Client - Interactive Mode")
        safe_print("=" * 60)
        safe_print(f"Platform: {self.client.platform_info['system']} {self.client.platform_info['release']}")
        safe_print(f"Connection: {self.client.connection_type or 'None'}")
        safe_print("Commands:")
        safe_print("  analyze [text] - Analyze text content")
        safe_print("  file [path] - Analyze a file")
        safe_print("  voice [text] - Voice and tone analysis")
        safe_print("  grammar [text] - Grammar analysis")
        safe_print("  terms [text] - Terminology analysis")
        safe_print("  access [text] - Accessibility analysis")
        safe_print("  improve [text] - Get improvement suggestions")
        safe_print("  guidelines [category] - Get style guidelines")
        safe_print("  search [query] - Search official style guide (web version)")
        safe_print("  guidance - Get official guidance for specific issues (web version)")
        safe_print("  help - Show this help")
        safe_print("  quit - Exit the program")
        safe_print("=" * 60)
        
        while True:
            try:
                user_input = input("\n📝 Enter command: ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split(None, 1)
                command = parts[0].lower()
                content = parts[1] if len(parts) > 1 else ""
                
                if command in ["quit", "exit", "q"]:
                    safe_print("👋 Goodbye!")
                    break
                
                elif command == "help":
                    await self._show_help()
                
                elif command == "analyze":
                    if not content:
                        content = input("Enter text to analyze: ")
                    await self._handle_analyze(content, "comprehensive")
                
                elif command == "file":
                    if not content:
                        content = input("Enter file path: ")
                    await self._handle_file_analysis(content)
                
                elif command == "voice":
                    if not content:
                        content = input("Enter text for voice analysis: ")
                    await self._handle_analyze(content, "voice_tone")
                
                elif command == "grammar":
                    if not content:
                        content = input("Enter text for grammar analysis: ")
                    await self._handle_analyze(content, "grammar")
                
                elif command == "terms":
                    if not content:
                        content = input("Enter text for terminology analysis: ")
                    await self._handle_analyze(content, "terminology")
                
                elif command == "access":
                    if not content:
                        content = input("Enter text for accessibility analysis: ")
                    await self._handle_analyze(content, "accessibility")
                
                elif command == "improve":
                    if not content:
                        content = input("Enter text to improve: ")
                    await self._handle_improvements(content)
                
                elif command == "guidelines":
                    category = content or "all"
                    await self._handle_guidelines(category)
                
                elif command == "search":
                    if not content:
                        content = input("Enter search query for style guide: ")
                    await self._handle_search(content)
                
                elif command == "guidance":
                    issue_type = input("Enter issue type (voice_tone, grammar, terminology, accessibility): ")
                    specific_term = input("Enter specific term (optional): ")
                    await self._handle_official_guidance(issue_type, specific_term)
                
                else:
                    safe_print(f"❌ Unknown command: {command}. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                safe_print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                safe_print(f"❌ Error: {e}")
    
    async def _handle_analyze(self, text: str, analysis_type: str):
        """Handle analysis commands."""
        if not text.strip():
            safe_print("❌ No text provided")
            return
        
        safe_print(f"🔍 Analyzing content for {analysis_type.replace('_', ' ')}...")
        result = await self.client.analyze_content(text, analysis_type)
        
        if result["success"]:
            safe_print("✅ Analysis complete:")
            safe_print(self._format_result(result["result"]))
        else:
            safe_print(f"❌ Analysis failed: {result['error']}")
    
    async def _handle_file_analysis(self, file_path: str):
        """Handle file analysis."""
        if not file_path.strip():
            safe_print("❌ No file path provided")
            return
        
        safe_print(f"📄 Analyzing file: {file_path}")
        result = await self.vscode.analyze_file(file_path)
        
        if result["success"]:
            safe_print("✅ File analysis complete:")
            safe_print(self._format_result(result["result"]))
        else:
            safe_print(f"❌ File analysis failed: {result['error']}")
    
    async def _handle_improvements(self, text: str):
        """Handle improvement suggestions."""
        if not text.strip():
            safe_print("❌ No text provided")
            return
        
        safe_print("💡 Generating improvement suggestions...")
        result = await self.client.suggest_improvements(text)
        
        if result["success"]:
            safe_print("✅ Suggestions generated:")
            safe_print(self._format_result(result["result"]))
        else:
            safe_print(f"❌ Failed to generate suggestions: {result['error']}")
    
    async def _handle_guidelines(self, category: str):
        """Handle guidelines requests."""
        safe_print(f"📚 Getting {category} guidelines...")
        result = await self.client.get_style_guidelines(category)
        
        if result["success"]:
            safe_print("✅ Guidelines retrieved:")
            safe_print(self._format_result(result["result"]))
        else:
            safe_print(f"❌ Failed to get guidelines: {result['error']}")
    
    async def _handle_search(self, query: str):
        """Handle style guide search (web-enabled version only)."""
        if not query.strip():
            safe_print("❌ No search query provided")
            return
        
        safe_print(f"🔍 Searching Microsoft Style Guide for: {query}")
        result = await self.client.search_style_guide(query)
        
        if result["success"]:
            safe_print("✅ Search completed:")
            safe_print(self._format_result(result["result"]))
        else:
            safe_print(f"❌ Search failed: {result['error']}")
            if "tool" in result.get("error", "").lower():
                safe_print("💡 Note: Search requires the web-enabled server version")
    
    async def _handle_official_guidance(self, issue_type: str, specific_term: str):
        """Handle official guidance requests (web-enabled version only)."""
        safe_print(f"📖 Getting official guidance for {issue_type}...")
        result = await self.client.get_official_guidance(issue_type, specific_term)
        
        if result["success"]:
            safe_print("✅ Official guidance retrieved:")
            safe_print(self._format_result(result["result"]))
        else:
            safe_print(f"❌ Failed to get guidance: {result['error']}")
            if "tool" in result.get("error", "").lower():
                safe_print("💡 Note: Official guidance requires the web-enabled server version")
    
    def _format_result(self, result) -> str:
        """Format result for display."""
        if isinstance(result, dict):
            # Try to format structured results nicely
            if "summary" in result:
                return f"Summary: {result['summary']}"
            elif "assessment" in result:
                return f"Assessment: {result['assessment']}"
            else:
                return json.dumps(result, indent=2)
        else:
            return str(result)
    
    async def _show_help(self):
        """Show detailed help information."""
        help_text = f"""
📋 Microsoft Style Guide FastMCP Client Help
==========================================

Platform: {self.client.platform_info['system']} {self.client.platform_info['release']}
Connection: {self.client.connection_type or 'None'}
Available Tools: {len(self.client.available_tools)}

🎯 Analysis Commands:
  analyze [text]    - Comprehensive Microsoft Style Guide analysis
  voice [text]      - Voice and tone analysis (warm, crisp, helpful)
  grammar [text]    - Grammar and style analysis (active voice, clarity)
  terms [text]      - Terminology consistency check
  access [text]     - Accessibility and inclusive language check
  
📄 File Commands:
  file [path]       - Analyze a file (supports .md, .txt, .rst files)
  
💡 Improvement Commands:
  improve [text]    - Get specific improvement suggestions
  
📚 Reference Commands:
  guidelines        - Get all Microsoft Style Guide guidelines
  guidelines voice  - Get voice and tone guidelines only
  guidelines grammar - Get grammar guidelines only
  guidelines terms  - Get terminology guidelines only
  guidelines access - Get accessibility guidelines only
  
🌐 Web-Enabled Commands (web server only):
  search [query]    - Search official Microsoft Style Guide
  guidance          - Get official guidance for specific issues
  
🔧 Utility Commands:
  help             - Show this help
  quit             - Exit the program

🎯 Microsoft Style Guide Principles:
  • Warm and relaxed: Natural, conversational tone
  • Crisp and clear: Direct, scannable content  
  • Ready to help: Action-oriented, supportive guidance
  • Use active voice and second person (you)
  • Use inclusive, bias-free language
  • Keep sentences under 25 words
  • Use contractions for natural tone
        """
        safe_print(help_text)

def format_output_for_display(result: str) -> str:
    """Format the result for better console display."""
    if isinstance(result, dict):
        return json.dumps(result, indent=2)
    
    lines = str(result).split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('📋') or line.startswith('🎯') or line.startswith('📊'):
            formatted_lines.append(f"\n{line}")
        elif line.startswith('✅') or line.startswith('⚠️') or line.startswith('❌'):
            formatted_lines.append(f"  {line}")
        elif line and not line.startswith(' '):
            formatted_lines.append(line)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

async def main():
    """Main entry point for the client."""
    parser = argparse.ArgumentParser(
        description="Microsoft Style Guide FastMCP Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python mcp_client.py --mode interactive
  
  # Analyze a file
  python mcp_client.py --mode file --file README.md
  
  # Analyze text with FastMCP server
  python mcp_client.py --mode text --text "Your content here" --server mcp_server.py
  
  # Connect to HTTP server
  python mcp_client.py --mode interactive --server-url http://localhost:3000
  
  # GitHub Copilot Chat integration
  python mcp_client.py --mode copilot --command analyze --text "Content to analyze"
        """
    )
    
    parser.add_argument(
        "--server-script", "--server",
        default="mcp_server.py",
        help="Path to the FastMCP server script (default: mcp_server.py)"
    )
    parser.add_argument(
        "--server-url",
        help="URL of running FastMCP server (e.g., http://localhost:3000)"
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "file", "text", "copilot", "guidelines", "search"],
        default="interactive",
        help="Client mode (default: interactive)"
    )
    parser.add_argument(
        "--file",
        help="File to analyze (for file mode)"
    )
    parser.add_argument(
        "--text",
        help="Text to analyze (for text mode)"
    )
    parser.add_argument(
        "--command",
        help="Command for copilot mode (analyze, voice, grammar, etc.)"
    )
    parser.add_argument(
        "--analysis-type",
        choices=["comprehensive", "voice_tone", "grammar", "terminology", "accessibility"],
        default="comprehensive",
        help="Type of analysis to perform (default: comprehensive)"
    )
    parser.add_argument(
        "--query",
        help="Search query for search mode"
    )
    parser.add_argument(
        "--category",
        choices=["voice", "grammar", "terminology", "accessibility", "all"],
        default="all",
        help="Category for guidelines mode (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize client
    client = FastMCPClient()
    cli = CLIInterface(client)
    
    try:
        # Check if server script exists (if provided)
        server_path = None
        if args.server_script and Path(args.server_script).exists():
            server_path = args.server_script
        elif args.server_script:
            safe_print(f"❌ Error: Server script not found: {args.server_script}")
            if not args.server_url:
                safe_print(f"   Please ensure {args.server_script} exists or use --server-url")
                return 1
        
        # Connect to server
        safe_print(f"🔌 Connecting to Microsoft Style Guide FastMCP Server...")
        safe_print(f"   Platform: {client.platform_info['system']}")
        
        if not await client.connect(server_path, args.server_url):
            safe_print("❌ Failed to connect to FastMCP server")
            safe_print("   Tried methods:")
            if server_path:
                safe_print(f"   • Stdio: {server_path}")
            if args.server_url:
                safe_print(f"   • HTTP: {args.server_url}")
            else:
                safe_print("   • HTTP: http://localhost:3000 (default)")
            safe_print("   • Server startup: " + ("Yes" if server_path else "No"))
            return 1
        
        safe_print("✅ Connected successfully!")
        safe_print(f"   Connection type: {client.connection_type}")
        safe_print(f"   Available tools: {len(client.available_tools)}")
        
        # Run based on mode
        if args.mode == "interactive":
            await cli.run_interactive()
        
        elif args.mode == "file":
            if not args.file:
                safe_print("❌ Error: --file argument required for file mode")
                return 1
            
            result = await cli.vscode.analyze_file(args.file, args.analysis_type)
            if result["success"]:
                safe_print(format_output_for_display(result["result"]))
            else:
                safe_print(f"❌ Error: {result['error']}")
                return 1
        
        elif args.mode == "text":
            if not args.text:
                safe_print("❌ Error: --text argument required for text mode")
                return 1
            
            result = await client.analyze_content(args.text, args.analysis_type)
            if result["success"]:
                safe_print(format_output_for_display(result["result"]))
            else:
                safe_print(f"❌ Error: {result['error']}")
                return 1
        
        elif args.mode == "copilot":
            if not args.command:
                safe_print("❌ Error: --command argument required for copilot mode")
                return 1
            
            copilot_interface = GitHubCopilotInterface(client)
            result = await copilot_interface.process_chat_command(args.command, args.text or "")
            
            if result["success"]:
                safe_print(format_output_for_display(result["result"]))
            else:
                safe_print(f"❌ Error: {result['error']}")
                if "available_commands" in result:
                    safe_print("\n📋 Available commands:")
                    for cmd in result["available_commands"]:
                        safe_print(f"  • {cmd}")
                return 1
        
        elif args.mode == "search":
            if not args.query:
                safe_print("❌ Error: --query argument required for search mode")
                return 1
            
            result = await client.search_style_guide(args.query)
            if result["success"]:
                safe_print(format_output_for_display(result["result"]))
            else:
                safe_print(f"❌ Error: {result['error']}")
                return 1
        
        elif args.mode == "guidelines":
            result = await client.get_style_guidelines(args.category)
            if result["success"]:
                safe_print(format_output_for_display(result["result"]))
            else:
                safe_print(f"❌ Error: {result['error']}")
                return 1
        
        return 0
        
    except KeyboardInterrupt:
        safe_print("\n\n👋 Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        safe_print(f"❌ Unexpected error: {e}")
        return 1
    
    finally:
        # Disconnect from server
        await client.disconnect()

if __name__ == "__main__":
    # Ensure cross-platform async event loop handling
    if sys.platform == "win32":
        # Use ProactorEventLoop on Windows for better subprocess and file I/O support
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)