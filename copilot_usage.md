# GitHub Copilot Chat Integration Guide

Complete guide for using the Microsoft Style Guide FastMCP server with GitHub Copilot Chat in VS Code.

## 🚀 Quick Start

Once the FastMCP server is set up, you can immediately start using it in GitHub Copilot Chat with natural language commands.

## 💬 Natural Language Commands

### Content Analysis

**Analyze entire documents:**
```
@workspace analyze this document for Microsoft Style Guide compliance
```

**Analyze specific text:**
```
@workspace analyze this content for Microsoft Style Guide compliance:
"Welcome to our new product! You can easily configure the settings to meet your needs."
```

**Quick style check:**
```
@workspace check if this follows Microsoft style guide:
"Users should utilize the functionality to facilitate optimal performance."
```

### Voice and Tone Analysis

**Check voice and tone:**
```
@workspace check the voice and tone of this text:
"The configuration of settings can be accomplished by the user through the interface."
```

**Evaluate warmth and clarity:**
```
@workspace evaluate how warm and clear this writing is:
"You'll need to setup your account before you can login to the system."
```

### Improvement Suggestions

**General improvements:**
```
@workspace suggest improvements for this writing:
"The utilization of this functionality can be leveraged to facilitate implementation."
```

**Focus on specific areas:**
```
@workspace suggest voice and tone improvements for:
"Users are advised that the configuration might require consideration of implications."
```

**Make text more conversational:**
```
@workspace make this text more conversational and Microsoft-style friendly:
"The administrator should configure the system parameters prior to deployment."
```

### Style Guidelines

**Get general guidelines:**
```
@workspace show me Microsoft Style Guide principles
```

**Specific category guidelines:**
```
@workspace show Microsoft Style Guide guidelines for voice and tone
```

**Accessibility guidelines:**
```
@workspace what are the Microsoft Style Guide rules for inclusive language?
```

**Terminology standards:**
```
@workspace show me Microsoft approved terminology for technical writing
```

## 🎯 Specific Use Cases

### Reviewing Documentation

**Review README files:**
```
@workspace review this README for Microsoft Style Guide compliance and suggest improvements
```

**Check API documentation:**
```
@workspace analyze this API documentation for clarity and Microsoft style:
[paste your API docs]
```

### Improving Marketing Copy

**Marketing content analysis:**
```
@workspace check if this marketing copy follows Microsoft's warm and helpful voice:
"Leverage our cutting-edge solutions to optimize your workflow efficiency."
```

**Make copy more engaging:**
```
@workspace make this product description more engaging using Microsoft style principles:
"This software provides functionality for user management."
```

### Code Comments and Documentation

**Analyze code comments:**
```
@workspace check these code comments for Microsoft style compliance:
// This function utilizes the API to facilitate data retrieval
```

**Improve technical explanations:**
```
@workspace improve this technical explanation using Microsoft style guide:
"The implementation leverages advanced algorithms to optimize performance metrics."
```

## 🔧 Advanced Commands

### Batch Analysis

**Analyze multiple sections:**
```
@workspace analyze each of these sections for Microsoft Style Guide compliance:

1. "Welcome to our platform"
2. "Configure your settings" 
3. "Contact support for assistance"
```

### Comparative Analysis

**Before and after comparison:**
```
@workspace compare these two versions for Microsoft style compliance:

Original: "Users should utilize the interface to facilitate configuration."
Revised: "You can use the interface to configure your settings."
```

### Specific Issue Checking

**Check for passive voice:**
```
@workspace check this text for passive voice issues:
"The settings can be configured by the user through the admin panel."
```

**Check for inclusive language:**
```
@workspace check this text for inclusive language issues:
"Hey guys, this feature is pretty crazy! The master configuration controls everything."
```

## 📊 Understanding Responses

### Analysis Results Format

When you run analysis commands, you'll get responses like:

```
📋 Microsoft Style Guide Analysis

✅ Good - Minor improvements suggested

📊 Text Statistics:
   • Words: 32
   • Sentences: 2  
   • Avg words/sentence: 16.0

🔍 Issues Found: 2
   • Voice/Tone: Use more contractions for natural tone
   • Terminology: Use "sign in" instead of "login"

✅ Positive Elements: 1
   • Good use of "you" (3 instances) - directly engages readers

🌐 Official Guidelines: https://learn.microsoft.com/en-us/style-guide
```

### Improvement Suggestions Format

```
💡 Microsoft Style Guide Improvement Suggestions

Text: "Users should utilize the functionality..."
Focus Area: All
Total Improvements: 3

Specific Improvements:
1. ⚠️ Voice/Tone: Replace "utilize" with "use" for simpler language
2. ⚠️ Grammar: Change "should" to direct instruction
3. ℹ️ Clarity: Address readers as "you" instead of "users"

📚 Reference: https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice
```

## 🎨 Creative Commands

### Style Translation

**Translate formal to friendly:**
```
@workspace rewrite this in Microsoft's warm and relaxed style:
"Please be advised that system maintenance will be conducted on the aforementioned date."
```

**Make instructions more action-oriented:**
```
@workspace make these instructions more action-oriented and helpful:
"The user may wish to consider configuring the optional settings."
```

### Voice Matching

**Match Microsoft's voice:**
```
@workspace rewrite this to match Microsoft's brand voice:
"Our revolutionary platform enables enterprises to leverage cutting-edge technologies."
```

## 🔄 Iterative Improvement

### Progressive Enhancement

1. **Initial analysis:**
   ```
   @workspace analyze this content for Microsoft Style Guide compliance:
   "The configuration process can be initiated by users through the administrative interface."
   ```

2. **Apply suggestions:**
   ```
   @workspace improve this based on the previous analysis:
   "You can start the configuration process through the admin interface."
   ```

3. **Final check:**
   ```
   @workspace final style check on this improved version:
   "You can start configuring your settings in the admin interface."
   ```

## 🛠️ Troubleshooting Chat Commands

### If Commands Don't Work

**Check server status:**
```
@workspace is the Microsoft Style Guide server running?
```

**Verify tools are available:**
```
@workspace what Microsoft Style Guide tools are available?
```

**Test basic functionality:**
```
@workspace test the style guide analysis with: "Hello, you can easily set up your account!"
```

### Alternative Command Formats

If the natural language approach doesn't work, try direct tool calls:

```
@workspace use analyze_content tool on: "Your text here"
```

```
@workspace use suggest_improvements tool with focus on voice and tone: "Your text here"
```

## 📝 Best Practices

### Effective Prompting

1. **Be specific about what you want:**
   - ✅ "check voice and tone of this marketing copy"
   - ❌ "analyze this"

2. **Include the content directly:**
   - ✅ Include text in quotes or code blocks
   - ❌ Reference content without showing it

3. **Specify focus areas when needed:**
   - ✅ "check for inclusive language issues"
   - ✅ "focus on grammar and clarity"

### Workflow Integration

1. **Draft → Analyze → Improve → Final Check**
2. **Use during code reviews for comments**
3. **Apply to documentation before publishing**
4. **Check marketing copy before approval**

## 🎯 Real-World Examples

### Technical Documentation

**Before:**
```
@workspace analyze: "The API facilitates the retrieval of user data through RESTful endpoints."
```

**After applying suggestions:**
```
@workspace final check: "You can get user data through our REST API endpoints."
```

### User Interface Text

**Before:**
```
@workspace check: "An error has occurred. Please contact the administrator."
```

**After improvement:**
```
@workspace verify: "Something went wrong. We're here to help - contact support anytime."
```

### Email Communication

**Before:**
```
@workspace improve: "We regret to inform you that the requested functionality is not currently available."
```

**After enhancement:**
```
@workspace final review: "Thanks for your interest! This feature isn't available yet, but we're working on it."
```

---

## 📞 Getting Help

If you need help with specific commands or scenarios:

1. Check this guide for similar examples
2. Try simpler, more direct commands
3. Verify the MCP server is running in VS Code
4. Test with basic examples first

The FastMCP server is designed to understand natural language, so feel free to experiment with different ways of asking for style analysis and improvements!