#!/usr/bin/env python3
"""
Microsoft Style Guide MCP Server - FastMCP Cross-Platform Version

A simplified, cross-platform MCP server using FastMCP for analyzing content 
against the official Microsoft Writing Style Guide.

This version provides the same functionality as the original but with:
- Simplified setup and dependencies
- Cross-platform compatibility
- Automatic VS Code integration
- Built-in Copilot Chat support
"""

import asyncio
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try FastMCP first, fall back to basic implementation
try:
    from fastmcp import FastMCP
    MCP_AVAILABLE = True
    logger.info("FastMCP library detected - enhanced functionality available")
except ImportError:
    try:
        # Try regular MCP
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import TextContent, CallToolResult, ListToolsResult, Tool, Resource
        MCP_AVAILABLE = True
        logger.info("Standard MCP library detected")
    except ImportError:
        MCP_AVAILABLE = False
        logger.info("No MCP library found - using development mode")

class MicrosoftStyleGuideAnalyzer:
    """Core analyzer for Microsoft Style Guide compliance."""
    
    def __init__(self):
        """Initialize the analyzer with pattern matching capabilities."""
        self.style_guide_base_url = "https://learn.microsoft.com/en-us/style-guide"
        
        # Core style patterns
        self.patterns = {
            "contractions": r"\b(it's|you're|we're|don't|can't|won't|let's|you'll|we'll)\b",
            "passive_voice": r"\b(is|are|was|were|been|be)\s+\w*ed\b",
            "long_sentences": r"[.!?]+\s*[A-Z][^.!?]{100,}[.!?]",
            "gendered_pronouns": r"\b(he|him|his|she|her|hers)\b",
            "non_inclusive_terms": r"\b(guys|mankind|blacklist|whitelist|master|slave|crazy|insane|lame)\b",
            "you_addressing": r"\byou\b",
            "second_person_avoid": r"\b(the user|users|one should|people should)\b"
        }
        
        # Microsoft terminology standards
        self.terminology_standards = {
            "AI": {"correct": "AI", "avoid": ["A.I."], "note": "No periods"},
            "email": {"correct": "email", "avoid": ["e-mail"], "note": "One word"},
            "website": {"correct": "website", "avoid": ["web site"], "note": "One word"},
            "sign_in": {"correct": "sign in (verb), sign-in (noun)", "avoid": ["login", "log in"], "note": "Microsoft standard"},
            "setup": {"correct": "set up (verb), setup (noun)", "avoid": ["setup (verb)"], "note": "Context dependent"},
            "wifi": {"correct": "Wi-Fi", "avoid": ["WiFi", "wifi"], "note": "Hyphenated, both caps"}
        }

    def analyze_content(self, text: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze text content against Microsoft Style Guide principles."""
        issues = []
        suggestions = []
        
        # Basic statistics
        words = text.split()
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        word_count = len(words)
        sentence_count = len(sentences)
        avg_words_per_sentence = round(word_count / max(1, sentence_count), 1)
        
        # Voice and tone analysis
        if analysis_type in ["comprehensive", "voice_tone"]:
            contractions = len(re.findall(self.patterns["contractions"], text, re.IGNORECASE))
            you_usage = len(re.findall(self.patterns["you_addressing"], text, re.IGNORECASE))
            
            if contractions > 0:
                suggestions.append({
                    "type": "positive",
                    "message": f"Good use of contractions ({contractions} found) - supports warm, natural tone",
                    "principle": "warm_and_relaxed"
                })
            else:
                issues.append({
                    "type": "voice_tone",
                    "severity": "info",
                    "message": "Consider using contractions (it's, you're, we'll) for a more natural tone",
                    "principle": "warm_and_relaxed"
                })
            
            if you_usage > 0:
                suggestions.append({
                    "type": "positive",
                    "message": f"Good use of 'you' ({you_usage} instances) - directly engages readers",
                    "principle": "ready_to_help"
                })
        
        # Grammar analysis
        if analysis_type in ["comprehensive", "grammar"]:
            # Passive voice
            passive_matches = list(re.finditer(self.patterns["passive_voice"], text, re.IGNORECASE))
            for match in passive_matches:
                issues.append({
                    "type": "grammar",
                    "severity": "warning",
                    "position": match.start(),
                    "text": match.group(),
                    "message": "Consider using active voice for clarity",
                    "principle": "crisp_and_clear"
                })
            
            # Long sentences
            long_sentences = list(re.finditer(self.patterns["long_sentences"], text))
            for match in long_sentences:
                issues.append({
                    "type": "grammar",
                    "severity": "info",
                    "position": match.start(),
                    "message": "Long sentence detected - consider breaking into shorter sentences",
                    "principle": "crisp_and_clear"
                })
        
        # Terminology analysis
        if analysis_type in ["comprehensive", "terminology"]:
            for term, standard in self.terminology_standards.items():
                for avoid_term in standard["avoid"]:
                    if avoid_term.lower() in text.lower():
                        issues.append({
                            "type": "terminology",
                            "severity": "warning",
                            "text": avoid_term,
                            "message": f"Use '{standard['correct']}' instead of '{avoid_term}'",
                            "note": standard["note"]
                        })
        
        # Accessibility analysis
        if analysis_type in ["comprehensive", "accessibility"]:
            # Non-inclusive language
            non_inclusive_matches = list(re.finditer(self.patterns["non_inclusive_terms"], text, re.IGNORECASE))
            for match in non_inclusive_matches:
                issues.append({
                    "type": "accessibility",
                    "severity": "error",
                    "position": match.start(),
                    "text": match.group(),
                    "message": f"'{match.group()}' may not be inclusive - consider alternatives",
                    "principle": "bias_free_communication"
                })
            
            # Gendered pronouns
            gendered_matches = list(re.finditer(self.patterns["gendered_pronouns"], text, re.IGNORECASE))
            for match in gendered_matches:
                issues.append({
                    "type": "accessibility",
                    "severity": "warning",
                    "position": match.start(),
                    "text": match.group(),
                    "message": "Consider gender-neutral alternatives",
                    "principle": "bias_free_communication"
                })
        
        # Generate overall assessment
        total_issues = len(issues)
        if total_issues == 0:
            status = "✅ Excellent"
            assessment = "Content follows Microsoft Style Guide principles well"
        elif total_issues <= 2:
            status = "⚠️ Good"
            assessment = "Minor style improvements suggested"
        else:
            status = "❌ Needs Work"
            assessment = "Multiple style issues detected"
        
        return {
            "status": status,
            "assessment": assessment,
            "statistics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_words_per_sentence": avg_words_per_sentence
            },
            "issues": issues,
            "suggestions": suggestions,
            "total_issues": total_issues,
            "analysis_type": analysis_type,
            "style_guide_url": self.style_guide_base_url
        }

    def get_style_guidelines(self, category: str = "all") -> Dict[str, Any]:
        """Get Microsoft Style Guide guidelines for a specific category."""
        guidelines = {
            "category": category,
            "base_url": self.style_guide_base_url,
            "principles": {}
        }
        
        if category in ["voice", "all"]:
            guidelines["principles"]["voice_and_tone"] = {
                "warm_and_relaxed": [
                    "Use contractions (it's, you're, we'll)",
                    "Write like you speak - natural, conversational",
                    "Be friendly and approachable"
                ],
                "crisp_and_clear": [
                    "Be direct and scannable",
                    "Keep sentences under 25 words",
                    "Use simple, clear language"
                ],
                "ready_to_help": [
                    "Use action-oriented language",
                    "Address readers as 'you'",
                    "Be supportive and encouraging"
                ]
            }
        
        if category in ["grammar", "all"]:
            guidelines["principles"]["grammar"] = {
                "active_voice": "Use active voice for clarity and engagement",
                "sentence_structure": "Keep sentences short and parallel",
                "imperative_mood": "Use for instructions (Click, Choose, Select)"
            }
        
        if category in ["terminology", "all"]:
            guidelines["principles"]["terminology"] = self.terminology_standards
        
        if category in ["accessibility", "all"]:
            guidelines["principles"]["accessibility"] = {
                "inclusive_language": [
                    "Use 'everyone' instead of 'guys'",
                    "Use 'allow list' instead of 'whitelist'",
                    "Use 'primary/secondary' instead of 'master/slave'"
                ],
                "people_first": "Use 'people with disabilities' not 'disabled people'",
                "gender_neutral": "Avoid gendered pronouns in generic references"
            }
        
        return guidelines

    def suggest_improvements(self, text: str, focus_area: str = "all") -> Dict[str, Any]:
        """Generate specific improvement suggestions for the text."""
        analysis = self.analyze_content(text, "comprehensive")
        improvements = []
        
        for issue in analysis["issues"]:
            if focus_area == "all" or issue["type"] == focus_area:
                improvement = {
                    "issue": issue["message"],
                    "suggestion": self._get_improvement_suggestion(issue),
                    "type": issue["type"],
                    "severity": issue["severity"]
                }
                improvements.append(improvement)
        
        # Add general improvements
        if analysis["statistics"]["avg_words_per_sentence"] > 25:
            improvements.append({
                "issue": "Average sentence length is high",
                "suggestion": "Break long sentences into shorter, clearer ones",
                "type": "grammar",
                "severity": "info"
            })
        
        return {
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "total_improvements": len(improvements),
            "improvements": improvements,
            "focus_area": focus_area,
            "style_guide_url": f"{self.style_guide_base_url}/top-10-tips-style-voice"
        }
    
    def _get_improvement_suggestion(self, issue: Dict[str, Any]) -> str:
        """Generate specific improvement suggestion based on issue type."""
        issue_type = issue["type"]
        
        if issue_type == "voice_tone":
            return "Use more contractions and direct language to sound natural and friendly"
        elif issue_type == "grammar" and "passive" in issue["message"]:
            return f"Change '{issue.get('text', '')}' to active voice"
        elif issue_type == "terminology":
            return f"Replace with Microsoft-approved term as noted"
        elif issue_type == "accessibility":
            return f"Use inclusive alternative for '{issue.get('text', '')}'"
        else:
            return "Follow Microsoft Style Guide recommendations"

# Initialize the analyzer
analyzer = MicrosoftStyleGuideAnalyzer()

# FastMCP Server Implementation
if MCP_AVAILABLE:
    try:
        # Try FastMCP first
        app = FastMCP("Microsoft Style Guide")
        
        @app.tool()
        def analyze_content(text: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
            """Analyze content against Microsoft Style Guide principles."""
            if not text.strip():
                return {"error": "No text provided for analysis"}
            
            result = analyzer.analyze_content(text, analysis_type)
            
            # Format for display
            summary = f"""📋 Microsoft Style Guide Analysis

{result['status']} - {result['assessment']}

📊 **Text Statistics:**
   • Words: {result['statistics']['word_count']}
   • Sentences: {result['statistics']['sentence_count']}
   • Avg words/sentence: {result['statistics']['avg_words_per_sentence']}

🔍 **Issues Found:** {result['total_issues']}"""
            
            if result['issues']:
                issues_by_type = {}
                for issue in result['issues']:
                    issue_type = issue['type']
                    if issue_type not in issues_by_type:
                        issues_by_type[issue_type] = []
                    issues_by_type[issue_type].append(issue)
                
                for issue_type, issues_list in issues_by_type.items():
                    summary += f"\n   • {issue_type.replace('_', ' ').title()}: {len(issues_list)}"
            
            if result['suggestions']:
                summary += f"\n\n✅ **Positive Elements:** {len(result['suggestions'])}"
            
            summary += f"\n\n🌐 **Official Guidelines:** {result['style_guide_url']}"
            
            return {"summary": summary, "detailed": result}
        
        @app.tool()
        def get_style_guidelines(category: str = "all") -> Dict[str, Any]:
            """Get Microsoft Style Guide guidelines for a specific category."""
            guidelines = analyzer.get_style_guidelines(category)
            
            # Format for display
            response = f"""📚 Microsoft Writing Style Guide - {category.title()} Guidelines

🌐 **Official Documentation:** {guidelines['base_url']}

"""
            
            for principle_name, principle_data in guidelines['principles'].items():
                response += f"## {principle_name.replace('_', ' ').title()}\n\n"
                
                if isinstance(principle_data, dict):
                    for key, value in principle_data.items():
                        response += f"**{key.replace('_', ' ').title()}:**\n"
                        if isinstance(value, list):
                            for item in value:
                                response += f"• {item}\n"
                        else:
                            response += f"• {value}\n"
                        response += "\n"
                elif isinstance(principle_data, str):
                    response += f"• {principle_data}\n\n"
            
            return {"formatted": response, "data": guidelines}
        
        @app.tool()
        def suggest_improvements(text: str, focus_area: str = "all") -> Dict[str, Any]:
            """Get improvement suggestions for content."""
            if not text.strip():
                return {"error": "No text provided for improvement suggestions"}
            
            improvements = analyzer.suggest_improvements(text, focus_area)
            
            # Format for display
            response = f"""💡 Microsoft Style Guide Improvement Suggestions

**Text:** "{improvements['text_preview']}"
**Focus Area:** {focus_area.replace('_', ' ').title()}
**Total Improvements:** {improvements['total_improvements']}

"""
            
            if improvements['improvements']:
                response += "**Specific Improvements:**\n"
                for i, improvement in enumerate(improvements['improvements'], 1):
                    severity_icon = "🔴" if improvement['severity'] == "error" else "⚠️" if improvement['severity'] == "warning" else "ℹ️"
                    response += f"{i}. {severity_icon} **{improvement['type'].replace('_', ' ').title()}:** {improvement['suggestion']}\n"
                response += "\n"
            else:
                response += "✅ **No improvements needed** - content follows Microsoft Style Guide well!\n\n"
            
            response += f"📚 **Reference:** {improvements['style_guide_url']}"
            
            return {"formatted": response, "data": improvements}
        
        @app.tool()
        def search_style_guide(query: str) -> Dict[str, Any]:
            """Search Microsoft Style Guide for specific guidance."""
            if not query.strip():
                return {"error": "No search query provided"}
            
            # Provide search guidance and relevant URLs
            search_url = f"{analyzer.style_guide_base_url}/?search={query.replace(' ', '%20')}"
            
            response = f"""🔍 Microsoft Style Guide Search

**Query:** "{query}"

**Search URL:** {search_url}

**Key Resources:**
• Voice & Tone: {analyzer.style_guide_base_url}/brand-voice-above-all-simple-human
• Writing Tips: {analyzer.style_guide_base_url}/global-communications/writing-tips
• Bias-Free Communication: {analyzer.style_guide_base_url}/bias-free-communication
• A-Z Word List: {analyzer.style_guide_base_url}/a-z-word-list-term-collections
• Top 10 Tips: {analyzer.style_guide_base_url}/top-10-tips-style-voice

💡 **Tip:** Visit the search URL above for the most current guidance on your query.
"""
            
            return {"formatted": response, "search_url": search_url, "query": query}
    
    except NameError:
        # FastMCP not available, use standard MCP
        logger.info("FastMCP not available, using standard MCP implementation")
        MCP_AVAILABLE = False

# Fallback for when MCP is not available
if not MCP_AVAILABLE:
    class MockApp:
        def __init__(self, name):
            self.name = name
            self.tools = {}
        
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator
        
        async def run_stdio(self):
            print(f"Mock MCP server '{self.name}' running in development mode")
            print("Available tools:", list(self.tools.keys()))
            # Simple test
            if "analyze_content" in self.tools:
                result = self.tools["analyze_content"]("Hello, you can easily set up your account!")
                print("Test analysis:", result)
    
    app = MockApp("Microsoft Style Guide")
    
    # Add the same tools but as regular functions
    @app.tool()
    def analyze_content(text: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze content against Microsoft Style Guide principles."""
        if not text.strip():
            return {"error": "No text provided for analysis"}
        return analyzer.analyze_content(text, analysis_type)
    
    @app.tool()
    def get_style_guidelines(category: str = "all") -> Dict[str, Any]:
        """Get Microsoft Style Guide guidelines."""
        return analyzer.get_style_guidelines(category)
    
    @app.tool()
    def suggest_improvements(text: str, focus_area: str = "all") -> Dict[str, Any]:
        """Get improvement suggestions."""
        if not text.strip():
            return {"error": "No text provided"}
        return analyzer.suggest_improvements(text, focus_area)
    
    @app.tool()
    def search_style_guide(query: str) -> Dict[str, Any]:
        """Search Microsoft Style Guide."""
        if not query.strip():
            return {"error": "No query provided"}
        return {"query": query, "url": f"{analyzer.style_guide_base_url}/?search={query}"}

async def main():
    """Run the MCP server."""
    parser = argparse.ArgumentParser(description="Microsoft Style Guide MCP Server - FastMCP Version")
    parser.add_argument("--version", action="version", version="microsoft-style-guide-fastmcp 1.0.0")
    parser.add_argument("--test", action="store_true", help="Run a quick test")
    
    args = parser.parse_args()
    
    if args.test:
        # Run a quick test - use analyzer directly to avoid FastMCP tool wrapper issues
        test_text = "You can easily configure the settings to suit your needs."
        result = analyzer.analyze_content(test_text)
        print("Test Result:", json.dumps(result, indent=2))
        return
    
    logger.info("Starting Microsoft Style Guide MCP Server (FastMCP)")
    
    try:
        if hasattr(app, 'run_stdio_async'):
            # FastMCP
            await app.run_stdio_async()
        elif hasattr(app, 'run_stdio'):
            # Standard MCP
            await app.run_stdio()
        else:
            # Mock implementation
            await app.run_stdio()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())