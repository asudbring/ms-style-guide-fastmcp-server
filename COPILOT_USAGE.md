# GitHub Copilot Chat Integration Examples
## Server Version: Web-Enabled FastMCP Server

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

### Document Review (NEW!)
```
@workspace microsoft_document_reviewer "Getting Started with Azure Functions

Azure Functions is a serverless compute service that lets you run event-triggered code without having to explicitly provision or manage infrastructure. In this tutorial, you will learn how to create your first function.

## Prerequisites
- An Azure account with an active subscription
- Visual Studio Code installed
- The Azure Functions extension for VS Code

## Creating Your First Function
1. Open Visual Studio Code
2. Press Ctrl+Shift+P to open the command palette
3. Type 'Azure Functions: Create New Project' and select it
4. Choose a folder for your project
5. Select your preferred language (JavaScript, Python, C#, etc.)

Your function is now ready to deploy!" --document_type="tutorial" --target_audience="developer"
```

### Quick Document Review
```
@workspace microsoft_document_reviewer "This feature allows users to configure their settings easily. The configuration can be accomplished through the interface." --review_focus="voice_tone"
```

### API Documentation Review
```
@workspace microsoft_document_reviewer "POST /api/users
Creates a new user in the system.

Parameters:
- name (string): The user's full name
- email (string): The user's email address

Returns:
201 Created on success
400 Bad Request if validation fails" --document_type="api_docs" --target_audience="developer"
```

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

## Direct Script Usage

```bash
# Analyze content
python copilot_integration.py analyze "Your content here"

# Get improvements  
python copilot_integration.py improve "Text to improve"

# Get guidelines
python copilot_integration.py guidelines voice

# Live search (web version)
python copilot_integration.py search "active voice"

# Document review (NEW!)
python copilot_integration.py review "Your document content here --type=tutorial --audience=developer"
```

## Server Version: Web-Enabled FastMCP Server

🌐 **Web Features**: Live content from Microsoft Learn, always up-to-date guidance

## MCP Tools Available in VS Code

Once the MCP server is running, these tools are available:
- `analyze_content` - Comprehensive style analysis
- `get_style_guidelines` - Retrieve specific guidelines
- `suggest_improvements` - Get improvement suggestions
- `search_style_guide` - Search official documentation (live)
- `get_official_guidance` - Get live official guidance (web version)
- `microsoft_document_reviewer` - **NEW!** Comprehensive document review for technical writers

## Document Reviewer Features

The new `microsoft_document_reviewer` tool provides:

### 📊 Quality Assessment
- **Overall Quality Score** (1-10) with detailed breakdown
- **Voice & Tone Analysis** against Microsoft's three principles
- **Clarity Assessment** including readability metrics
- **Accessibility Review** for inclusive language
- **Compliance Check** against Microsoft terminology standards

### 🎯 Document Type Support
- `api_docs` - API documentation and reference materials
- `user_guide` - User manuals and how-to guides  
- `tutorial` - Step-by-step learning content
- `troubleshooting` - Problem-solving documentation
- `general` - General business or technical content

### 👥 Audience Targeting
- `developer` - Technical developers and engineers
- `end_user` - Non-technical end users
- `admin` - System administrators
- `mixed` - Multiple audience types
- `general` - General business audience

### 🔍 Review Focus Areas
- `voice_tone` - Microsoft voice and tone compliance
- `clarity` - Readability and comprehension
- `structure` - Document organization and flow
- `accessibility` - Inclusive language and barriers
- `all` - Comprehensive review (default)

### 📝 Output Includes
- **Executive Summary** with key findings
- **Quality Scores** for each assessment area
- **Detailed Analysis** of voice, clarity, UX, and compliance
- **Prioritized Recommendations** (High/Medium/Low priority)
- **Before/After Examples** showing specific improvements
- **Live Official Guidance** (web version only)

## Example Document Review Output

```
📋 Microsoft Style Guide Document Review (Web-Enabled)

## Executive Summary
Overall Quality Score: 7.2/10 (Good)
Document Type: Tutorial
Target Audience: Developer
Word Count: 156

### Key Strengths
✅ Good sentence length for readability
✅ Uses engaging, direct language effectively
✅ Strong Microsoft voice and tone compliance

### Critical Issues
🔴 No critical issues identified

### Recommended Next Steps
📌 Address medium-priority recommendations
📌 Review with stakeholders
📌 One more revision recommended

## Quality Scores
Voice & Tone: 8.5/10
Clarity: 7.0/10
Accessibility: 9.0/10
Compliance: 6.5/10

## Improvement Recommendations

### High Priority
🔴 No critical issues found

### Medium Priority
⚠️ Update terminology to match Microsoft standards
⚠️ Improve voice and tone to match Microsoft's warm, conversational style

### Low Priority
ℹ️ Add contractions to make tone more natural and conversational

## Rewrite Examples (Web-Enhanced)

### 1. Natural Tone
Before: You cannot access this feature.
After: You can't access this feature.
Why: Added contractions for a more natural, conversational tone
Official Guidance: Microsoft voice is warm and relaxed - use contractions to sound natural

🌐 Live Official Guidance Retrieved:
Voice/Tone: Microsoft's brand voice: above all, simple and human
📎 https://learn.microsoft.com/en-us/style-guide/brand-voice-above-all-simple-human
```

## Best Practices for Document Review

### 1. Choose the Right Document Type
- Use `tutorial` for step-by-step guides
- Use `api_docs` for technical reference
- Use `user_guide` for end-user documentation
- Use `troubleshooting` for problem-solving content

### 2. Specify Your Audience
- `developer` for technical content requiring code knowledge
- `end_user` for consumer-facing documentation
- `admin` for system administration guides
- `mixed` when content serves multiple audiences

### 3. Focus Your Review
- Use `voice_tone` for brand voice compliance
- Use `clarity` for readability concerns
- Use `accessibility` for inclusive language review
- Use `all` for comprehensive analysis (recommended)

### 4. Interpret Quality Scores
- **9-10**: Excellent - ready for publication
- **7-8**: Good - minor improvements needed
- **5-6**: Needs improvement - revision recommended
- **1-4**: Requires major revision

### 5. Prioritize Recommendations
1. **High Priority**: Fix immediately (accessibility, critical clarity issues)
2. **Medium Priority**: Address in next revision (voice, tone, structure)
3. **Low Priority**: Nice-to-have improvements (terminology, minor style)

## Integration with Technical Writing Workflows

### Pre-Publication Review
```bash
# Review final draft before publishing
@workspace microsoft_document_reviewer "$(cat final-draft.md)" --document_type="user_guide" --target_audience="end_user"
```

### API Documentation Validation
```bash
# Validate API docs for developers
@workspace microsoft_document_reviewer "$(cat api-reference.md)" --document_type="api_docs" --target_audience="developer" --review_focus="clarity"
```

### Tutorial Quality Check
```bash
# Check tutorial effectiveness
@workspace microsoft_document_reviewer "$(cat getting-started.md)" --document_type="tutorial" --target_audience="mixed"
```

### Accessibility Audit
```bash
# Focus on inclusive language
@workspace microsoft_document_reviewer "$(cat content.md)" --review_focus="accessibility"
```

This comprehensive document review system helps technical writers maintain Microsoft Style Guide compliance while improving content quality and user experience.
