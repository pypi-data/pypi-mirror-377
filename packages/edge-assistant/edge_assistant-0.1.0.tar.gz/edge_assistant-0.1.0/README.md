# edge-assistant

A unified multimodal CLI assistant for AI-powered research, content analysis, knowledge base management, and safe file editing. Built on OpenAI's latest Responses API with full threading support across text, images, and documents.

Quickstart
----------

1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the project in editable mode:

```bash
pip install --upgrade pip
pip install -e .
```

3. Configure your OpenAI key (choose one option):

**Option A: Environment variable**
```bash
export OPENAI_API_KEY="sk-..."
```

**Option B: .env file (recommended)**
```bash
echo 'OPENAI_API_KEY="sk-..."' > .env
```

4. See available commands:

```bash
edge-assistant --help
```

## Key Features

🔥 **Unified Multimodal Analysis** - Seamlessly work with text, images, PDFs, and documents in threaded conversations  
🧠 **Advanced Threading** - Maintain context across mixed content types with intelligent state management  
🔍 **Web Research** - Built-in web search with structured output and citations  
📚 **Knowledge Base** - Index and search local documents with vector embeddings  
✏️ **Safe Editing** - Preview file changes with unified diffs before applying  
🛠️ **Agent Mode** - Tool-calling AI with file system access and approval workflows  
⚡ **Latest API** - Built on OpenAI's Responses API for optimal performance and features

## Commands Overview

| Command | Description | Threading | Content Types |
|---------|-------------|-----------|---------------|
| `analyze` | **Unified multimodal analysis** | ✅ | Text, Images, PDFs, Documents |
| `ask` | Interactive text conversations | ✅ | Text |
| `research` | Web research with citations | ❌ | Text + Web Search |
| `kb-index` | Index documents for search | ❌ | Local Files |
| `kb-research` | Query knowledge base | ❌ | Text + KB Search |
| `edit` | Safe file editing with diffs | ❌ | Text + File Editing |
| `agent` | Tool-calling AI assistant | ❌ | Text + Tools |
| `analyze-image` | Legacy image analysis | ✅ | Images (deprecated) |

Examples
--------

### 🎯 Unified Multimodal Analysis (New!)

```bash
# Text-only analysis with threading
edge-assistant analyze "What are the key principles of good software architecture?" --thread project-review

# Image analysis with context
edge-assistant analyze "What safety issues do you see in this facility?" --file facility.jpg --thread project-review --system "You are a health and safety inspector"

# Continue conversation with document analysis
edge-assistant analyze "Based on our safety assessment, analyze this compliance report" --file report.pdf --thread project-review

# Mixed content conversation
edge-assistant analyze "Given everything we've discussed, what are your top 3 recommendations?" --thread project-review
```

### 🔍 Web Research

```bash
# Research with structured output and citations
edge-assistant research "latest developments in multimodal AI 2025"
edge-assistant research "best practices for RAG implementation"
```

### 💬 Interactive Conversations

```bash
# Text conversations with threading (now uses unified engine by default)
edge-assistant ask "Explain the difference between RAG and fine-tuning" --thread learning
edge-assistant ask "Can you give me examples of each approach?" --thread learning

# Use legacy engine if needed
edge-assistant ask "Simple question" --legacy
```

### 📚 Knowledge Base Management

```bash
# Index local documents for search
edge-assistant kb-index ./docs ./papers ./notes

# Search your indexed knowledge
edge-assistant kb-research "How does attention mechanism work in transformers?"
```

### ✏️ Safe File Editing

```bash
# Preview changes before applying (dry-run by default)
edge-assistant edit README.md "Add a quickstart section with installation instructions"

# Apply changes after review
edge-assistant edit README.md "Add a quickstart section" --apply
```

### 🛠️ Agent Mode with Tools

```bash
# Tool-calling AI with file system access
edge-assistant agent "Create a Python script that processes CSV files and generates plots" --approve
edge-assistant agent "Analyze the performance of my web app and suggest optimizations"
```

## 🎨 Multimodal Analysis Features

### Unified Content Support
- **📝 Text**: Natural language questions and conversations
- **🖼️ Images**: JPEG, PNG, GIF, WebP analysis with vision models
- **📄 Documents**: PDF, TXT, MD, code files with file search
- **🔜 Audio/Video**: Ready for future OpenAI capabilities

### Advanced Threading
- **Fresh Context (default)**: Each analysis is independent  
- **Threaded Conversations**: Use `--thread` to maintain context across any content types
- **Smart Limits**: Max 20 interactions per thread (configurable with `--max-interactions`)
- **Content Tracking**: Detailed breakdown by content type (text, image, file)
- **Auto-cleanup**: Old threads (7+ days) are automatically removed

### Thread Management
```bash
# Check thread status (shows interaction breakdown by content type)
edge-assistant analyze "Describe this" --file image.jpg --thread session
# Output: Thread 'session': 3 interactions (1 text, 2 image)

# Clear a specific thread
edge-assistant analyze --clear-thread --thread session

# Set custom interaction limit per thread  
edge-assistant analyze "Analyze this" --file doc.pdf --thread session --max-interactions 50

# Mix content types seamlessly in same thread
edge-assistant analyze "What are the main concepts?" --thread session                    # Text
edge-assistant analyze "How does this image relate?" --file chart.png --thread session  # Image  
edge-assistant analyze "What does this document say?" --file report.pdf --thread session # Document
```

### Specialized Analysis Use Cases
```bash
# Health & Safety Inspection Workflow
edge-assistant analyze "Assess safety compliance" --file facility.jpg --thread safety-audit --system "You are a health and safety inspector"
edge-assistant analyze "Review this incident report" --file report.pdf --thread safety-audit  
edge-assistant analyze "Based on our inspection and the report, what are your recommendations?" --thread safety-audit

# Document Analysis & OCR
edge-assistant analyze "Extract all text and key information" --file receipt.png --system "You are an OCR specialist with accounting expertise"
edge-assistant analyze "Summarize the financial data from the receipt" --thread expense-review

# Technical Architecture Review  
edge-assistant analyze "Explain this system architecture" --file diagram.png --system "You are a software architect"
edge-assistant analyze "Based on the diagram, what are potential scalability concerns?" --thread arch-review
edge-assistant analyze "Review this code for the same system" --file main.py --thread arch-review

# Research & Analysis Pipeline
edge-assistant analyze "What are the main themes in this research paper?" --file paper.pdf --thread research
edge-assistant analyze "How does this data visualization support the paper's claims?" --file chart.jpg --thread research
edge-assistant analyze "Synthesize the key findings and implications" --thread research
```

### Content Type Detection
The system automatically detects content types, but you can override:
```bash
# Auto-detection (default)
edge-assistant analyze "Analyze this" --file document.pdf --type auto

# Force specific type
edge-assistant analyze "Analyze as image" --file diagram.pdf --type image
edge-assistant analyze "Analyze as document" --file screenshot.png --type file
edge-assistant analyze "Text-only analysis" --type text
```

### Model Selection
```bash
# Auto-select optimal model based on content type (default)  
edge-assistant analyze "Question" --file content.jpg

# Override model selection
edge-assistant analyze "Question" --file image.jpg --model gpt-4o-mini
edge-assistant analyze "Question" --file document.pdf --model gpt-4o
```

## 🏗️ Architecture

### Core Components
- **`cli.py`** - Typer-based CLI interface with unified multimodal commands  
- **`engine.py`** - OpenAI Responses API wrapper with multimodal support and threading
- **`tools.py`** - Utility functions for diffs, text extraction, URL parsing, and function tools
- **`state.py`** - XDG-compliant state management with multimodal thread tracking

### Key Design Principles
- **API Consistency**: All content types use OpenAI Responses API for threading and state management
- **Backward Compatibility**: Legacy commands maintained while encouraging migration to unified interface  
- **Content Agnostic**: Same threading system works across text, images, documents, and future modalities
- **Smart Defaults**: Auto-detection and optimal model selection reduce cognitive overhead
- **Safety First**: Dry-run by default for destructive operations, with explicit approval workflows

### State Management
- **Thread Persistence**: XDG-compliant JSON storage with automatic cleanup
- **Content Tracking**: Detailed metadata per thread including content type breakdown
- **Cross-Modal Threading**: Seamless context preservation across different content types  
- **Legacy Support**: Backward compatibility with existing thread structures

### Responses API Integration
- **Unified Interface**: Single method handles text, images, documents via `analyze_multimodal_content()`
- **Proper Threading**: Uses `previous_response_id` for server-side state management
- **Content Detection**: Automatic file type detection with manual override capability
- **Future Ready**: Architecture prepared for audio, video, and other upcoming modalities

Dev Notes   
---------

### Dependencies
Core: `openai`, `typer`, `rich`, `platformdirs`, `python-dotenv`

### Environment Setup
```bash
# Create virtual environment  
python3 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install --upgrade pip && pip install -e .

# Configure API key
echo 'OPENAI_API_KEY="sk-..."' > .env
```

## 🧪 Testing

Run the test suite after installing test dependencies:

```bash
pip install pytest
pytest -q
```

The test suite includes CLI command validation and basic functionality tests using Typer's CliRunner.

## 🔄 Migration Guide

### From Legacy Commands

**Image Analysis**: The new `analyze` command replaces `analyze-image`:

```bash
# Old (still works but deprecated)
edge-assistant analyze-image image.jpg "Describe this" --thread session

# New (recommended)  
edge-assistant analyze "Describe this" --file image.jpg --thread session
```

**Enhanced Ask**: The `ask` command now uses the unified multimodal engine by default:

```bash
# Automatic (uses new engine)
edge-assistant ask "Question" --thread session

# Force legacy engine if needed
edge-assistant ask "Question" --thread session --legacy
```

### Thread Compatibility
- **Existing text threads**: Fully compatible with new multimodal system
- **Legacy vision threads**: Automatically migrated to new multimodal format  
- **Thread data**: All existing thread data preserved during migration

## 📋 Command Reference

```bash
# Get help for any command
edge-assistant --help
edge-assistant analyze --help
edge-assistant ask --help

# Version information  
edge-assistant --version
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the existing code style
4. Add tests for new functionality
5. Run the test suite: `pytest`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
