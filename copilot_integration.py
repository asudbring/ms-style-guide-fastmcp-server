#!/usr/bin/env python3
"""
GitHub Copilot Chat Integration for Microsoft Style Guide FastMCP Server
Server Version: Web - Live guidance from Microsoft Learn website

# Web-enabled version: includes live content fetching

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
        print(f"Server: Web-Enabled FastMCP Server")
        return
    
    command = sys.argv[1].lower()
    content = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    
    # Import and initialize the analyzer for direct tool access
    try:
        sys.path.append(str(Path(__file__).parent))
        
        # Try web version first (if configured), then fall back to offline
        if "web" == "web":
            try:
                from fastmcp_style_server_web import WebEnabledStyleGuideAnalyzer
                analyzer = WebEnabledStyleGuideAnalyzer()
                server_type = "web"
            except ImportError:
                from fastmcp_style_server import MicrosoftStyleGuideAnalyzer, search_style_guide
                analyzer = MicrosoftStyleGuideAnalyzer()
                server_type = "offline"
        else:
            from fastmcp_style_server import MicrosoftStyleGuideAnalyzer, search_style_guide
            analyzer = MicrosoftStyleGuideAnalyzer()
            server_type = "offline"
        
        if command in ["analyze", "check", "review"]:
            if not content:
                print("Error: No content provided for analysis")
                return
            if server_type == "web":
                result = await analyzer.analyze_content(content, "comprehensive")
            else:
                result = analyzer.analyze_content(content, "comprehensive")
            
        elif command in ["improve", "suggest", "fix"]:
            if not content:
                print("Error: No content provided for improvements")
                return
            if server_type == "web":
                result = await analyzer.suggest_improvements(content, "all")
            else:
                result = analyzer.suggest_improvements(content, "all")
            
        elif command in ["guidelines", "guide", "help"]:
            category = content or "all"
            result = analyzer.get_style_guidelines(category)
            
        elif command in ["search", "find"]:
            if not content:
                print("Error: No search query provided")
                return
            if server_type == "offline":
                result = search_style_guide(content)
            else:
                # For web version, use search capability if available
                result = {"status": "info", "message": "Search functionality varies by server version"}
            
        else:
            result = {
                "error": f"Unknown command: {command}",
                "available_commands": [
                    "analyze - Comprehensive style analysis",
                    "improve - Get improvement suggestions", 
                    "guidelines - Get style guidelines",
                    "search - Search style guide(live)"
                ],
                "server_version": "web",
                "server_type": "Web-Enabled FastMCP Server"
            }
        
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
        print(f"Error: Could not import FastMCP server: {e}")
        print("Please ensure both fastmcp_style_server.py and fastmcp_style_server_web.py are in the same directory")

if __name__ == "__main__":
    asyncio.run(main())
