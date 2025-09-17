# DocPrint Reference Guide

## Overview
DocPrint is a runtime documentation generation tool that creates live markdown output with intelligent caching, content deduplication, and optional GitHub integration.

## Installation

```bash
pip install docprint
```

**Optional performance dependencies:**
```bash
pip install docprint[performance]  # Includes ujson, orjson
```

**Manual performance installation:**
```bash
pip install regex xxhash orjson
```

## Quick Start

```python
from docprint import docPrint, flush_cache, docPrintFile, enableGitCommits

# Basic usage - writes to DOC.PRINT.md
docPrint('text', 'Status', 'Application started')

# Custom output file
docPrintFile("my_docs.md")
docPrint('header', 'Project Status', 'Ready for deployment')

# Optional GitHub integration
enableGitCommits(True, token="ghp_xxx", repo="user/repo")

# Automatic flushing every 30 seconds or 1000 calls
# Manual flush when needed
flush_cache()
```

## GitHub Integration

### Auto-sync Documentation
Automatically push documentation changes to GitHub at configurable intervals.

```python
from docprint import enableGitCommits, docPrint
import os

# Enable GitHub sync (requires personal access token)
enableGitCommits(True, token="ghp_xxx", repo="username/repository")

# Custom sync interval (minimum 1 minute)
enableGitCommits(True, 
                token="ghp_xxx", 
                repo="username/repository", 
                interval_minutes=5)

# Disable sync
enableGitCommits(False)
```

### Setup Requirements
- GitHub personal access token with repo permissions
- Target repository must exist and be accessible
- Respects API rate limits (1 request per minute maximum)

### Behavior
- Only pushes when content actually changes
- Uses content hashing to detect modifications
- Creates single commit per sync with message: `docs: update {filename} via DocPrint`
- Handles network failures gracefully
- Thread-safe operation

### Token Setup

**Environment variable (recommended):**
```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

**Direct usage:**
```python
import os
token = os.getenv('GITHUB_TOKEN')
enableGitCommits(True, token=token, repo="user/repo")
```

**Direct token (less secure):**
```python
enableGitCommits(True, token="ghp_xxx", repo="user/repo")
```

### Error Handling
```python
try:
    enableGitCommits(True, token="invalid", repo="test/repo")
except ValueError as e:
    print(f"GitHub setup failed: {e}")
```

### Usage Examples

**Basic automation:**
```python
# Set up once at startup
enableGitCommits(True, 
                token=os.getenv('GITHUB_TOKEN'), 
                repo="company/docs")

# Normal operation - auto-syncs every minute
docPrint('text', 'Server Status', 'Running')
docPrint('table', 'Metrics', performance_data)
# Changes sync automatically
```

**Development workflow:**
```python
# During development - faster sync
enableGitCommits(True, 
                token=token, 
                repo="dev/project-docs", 
                interval_minutes=2)

# Production - slower sync to reduce API calls
enableGitCommits(True, 
                token=token, 
                repo="prod/documentation", 
                interval_minutes=10)
```

**Conditional sync:**
```python
# Only enable in production
if os.getenv('ENVIRONMENT') == 'production':
    enableGitCommits(True, 
                    token=os.getenv('GITHUB_TOKEN'), 
                    repo="company/live-docs")
```

## File Management

### Default Output
By default, all content is written to `DOC.PRINT.md` in the current directory.

### Custom Output Files

```python
# Single file
docPrintFile("documentation.md")

# Create directory structure
docPrintFile("logs/app.log")
docPrintFile("reports/daily/status.md") 
docPrintFile("project/docs/api.md")

# Reset to default
docPrintFile("")  # Returns to DOC.PRINT.md
```

**File switching:**
- Flushes current cache before switching files
- Creates directories automatically
- Thread-safe file operations
- Atomic file writes prevent corruption

## Available Formatters

### Basic Content Types

#### Header
```python
docPrint('header', 'Section Title', 'Optional description')
```

## Section Title

Optional description

---

#### Text
```python
docPrint('text', 'Status', 'System operational', line=True)
```

## Status

System operational

---

#### Table
```python
docPrint('table', 'Performance Data', [
    {'metric': 'CPU', 'value': '45%'},
    {'metric': 'Memory', 'value': '2.1GB'}
])
```

## Performance Data

| metric | value |
|---|---|
| CPU | 45% |
| Memory | 2.1GB |

---

#### Table with Alignment
```python
docPrint('advanced_table', 'User Data', {
    'headers': ['Name', 'Age', 'Score'],
    'alignment': ['left', 'center', 'right'],
    'rows': [
        ['Alice', 25, 95.5],
        ['Bob', 30, 88.2],
        ['Charlie', 28, 92.0]
    ]
})
```

## User Data

| Name | Age | Score |
|---|:---:|---:|
| Alice | 25 | 95.5 |
| Bob | 30 | 88.2 |
| Charlie | 28 | 92.0 |

---

### Structural Elements

#### Bullets
```python
docPrint('bullets', 'Key Points', ['First point', 'Second point', 'Third point'])
```

## Key Points

- First point
- Second point
- Third point

---

#### Horizontal Rule
```python
docPrint('horizontal_rule', 'Section Break', 'Content above the line')
```

## Section Break

Content above the line

---

---

#### Code Block
```python
docPrint('code_block', 'Python Example', 'print("Hello World")', language='python')
```

## Python Example

```python
print("Hello World")
```

---

#### Blockquote
```python
docPrint('blockquote', 'Quote', 'This is important text')
```

## Quote

> This is important text

---

#### Ordered List
```python
docPrint('ordered_list', 'Steps', ['Step 1', 'Step 2', 'Step 3'])
```

## Steps

1. Step 1
2. Step 2
3. Step 3

---

#### Unordered List
```python
docPrint('unordered_list', 'Items', ['Item A', 'Item B', 'Item C'])
```

## Items

- Item A
- Item B
- Item C

---

#### Footnotes
```python
docPrint('footnotes', 'Research Paper', 
         ("This study builds on previous work", 
          {1: "Source: Smith et al. 2020", 2: "Additional data from Johnson study"}))
```

## Research Paper

This study builds on previous work[^1][^2]

[^1]: Source: Smith et al. 2020
[^2]: Additional data from Johnson study

---

#### Definition List
```python
docPrint('definition_list', 'Glossary', {
    "API": "Application Programming Interface",
    "JSON": "JavaScript Object Notation"
})
```

## Glossary

API
: Application Programming Interface

JSON
: JavaScript Object Notation

---

#### Task List
```python
docPrint('task_list', 'Checklist', [
    {"task": "Write documentation", "completed": True},
    {"task": "Test features", "completed": False}
])
```

## Checklist

- [x] Write documentation
- [ ] Test features

---

### Visual Elements

#### Badge
```python
docPrint('badge', 'Build Status', {
    'label': 'build',
    'message': 'passing',
    'color': 'green',
    'style': 'flat',
    'url': 'https://github.com/repo'
})
```

## Build Status

[![build](https://img.shields.io/badge/build-passing-green?style=flat)](https://github.com/repo)

---

#### HTML Block
```python
docPrint('html_block', 'Custom HTML', {
    'tag': 'div',
    'attributes': {'class': 'highlight', 'id': 'test-div'},
    'content': 'This is custom HTML content'
})
```

## Custom HTML

<div class="highlight" id="test-div">
This is custom HTML content
</div>

---

#### CSS Block
```python
docPrint('css_block', 'Styling', {
    'selector': '.highlight',
    'styles': {
        'background-color': 'yellow',
        'padding': '10px',
        'border-radius': '5px'
    }
})
```

## Styling

```css
.highlight {
  background-color: yellow;
  padding: 10px;
  border-radius: 5px;
}
```

---

#### SVG Animation
```python
docPrint('svg_animation', 'Loading Spinner', {
    'width': 50,
    'height': 50,
    'elements': [{
        'tag': 'circle',
        'attributes': {'cx': 25, 'cy': 25, 'r': 10, 'fill': 'blue'},
        'animations': [{
            'attributeName': 'r',
            'values': '5;15;5',
            'dur': '1s',
            'repeatCount': 'indefinite'
        }]
    }]
})
```

## Loading Spinner

<svg width="50" height="50" xmlns="http://www.w3.org/2000/svg">
  <circle cx="25" cy="25" r="10" fill="blue">
    <animate attributeName="r" values="5;15;5" dur="1s" repeatCount="indefinite" />
  </circle>
</svg>

---

### Rich Content

#### Alert
```python
docPrint('alert', 'Warning', 'This is important', alert_type='warning')
docPrint('alert', 'Error List', ['Error 1', 'Error 2'], alert_type='error')
```

Alert types: `info`, `warning`, `error`, `success`, `note`

## Warning

> **[WARNING]**
>
> This is important

## Error List

> **[ERROR]**
>
> Error 1
> Error 2

---

#### Collapsible Section
```python
docPrint('collapsible', 'Details', 'Hidden content', summary='Click to expand')
```

## Details

<details>
<summary>Click to expand</summary>

Hidden content

</details>

---

#### Image
```python
docPrint('image', 'Logo', {
    'url': 'https://example.com/logo.png',
    'alt': 'Company Logo',
    'title': 'Our Logo',
    'width': '200',
    'height': '100'
})

# Simple version
docPrint('image', 'Simple Image', 'https://example.com/image.jpg')
```

## Logo

<img src="https://example.com/logo.png" alt="Company Logo" width="200" height="100" title="Our Logo" />

## Simple Image

![Image](https://example.com/image.jpg)

---

#### Link Collection
```python
docPrint('link_collection', 'Resources', [
    {'url': 'https://github.com', 'text': 'GitHub', 'description': 'Code repository'},
    {'url': 'https://docs.python.org', 'text': 'Python Docs'}
])
```

## Resources

- [GitHub](https://github.com) - Code repository
- [Python Docs](https://docs.python.org)

---

## Function Reference

### docPrint(section_type, header, content="", line=True, **kwargs)
Generate and cache formatted content.

**Parameters:**
- `section_type`: Formatter to use (see Available Formatters)
- `header`: Section header text
- `content`: Main content (string, list, or dict depending on type)
- `line`: Add separator line after content (default: True)
- `**kwargs`: Type-specific parameters

**Type-specific Parameters:**
- `language`: Code block syntax highlighting
- `alert_type`: Alert style (info, warning, error, success, note)
- `summary`: Collapsible section summary text
- `alignment`: Table column alignment (['left', 'center', 'right'])

### docPrintFile(filepath)
Set output file for subsequent docPrint calls.

**Parameters:**
- `filepath`: Target file path (creates directories as needed)
- Empty string or None resets to default (DOC.PRINT.md)

### flush_cache()
Force write cached content to file immediately.

### enableGitCommits(enabled, **kwargs)
Enable or disable automatic GitHub synchronization.

**Parameters:**
- `enabled`: Boolean to enable/disable GitHub sync
- `token`: GitHub personal access token (required when enabled)
- `repo`: Repository in format "username/repository" (required when enabled)
- `interval_minutes`: Sync interval in minutes, minimum 1 (default: 1)

**Examples:**
```python
# Enable with defaults
enableGitCommits(True, token="ghp_xxx", repo="user/repo")

# Custom interval
enableGitCommits(True, token="ghp_xxx", repo="user/repo", interval_minutes=5)

# Disable
enableGitCommits(False)
```

**Raises:**
- `ValueError`: Invalid token, repository access denied, or missing parameters
- `ImportError`: GitHub integration not available (should not occur in normal installations)

**Notes:**
- Validates repository access before enabling
- Only one sync configuration active at a time
- Disabling clears any existing sync timers
- Changes sync to currently configured output file

## Performance Features

### Smart Caching
- **Content deduplication**: Identical content is automatically deduplicated
- **Hash-based comparison**: Uses xxhash (fast) or MD5 (fallback) for content comparison
- **Zero redundant I/O**: Repeated identical content doesn't trigger file writes

### Optimized I/O
- **Memory-mapped files**: Large files (>1MB) use mmap for better performance
- **Atomic writes**: Temporary files with atomic replacement prevent corruption
- **Thread-safe operations**: RLock protection for concurrent access
- **Efficient path operations**: Uses pathlib.Path for cross-platform compatibility

### Auto-flush Behavior
- **Time-based**: Every 30 seconds
- **Count-based**: Every 1000 docPrint calls
- **Only when needed**: Empty cache skips I/O operations

## Content Management

### Content Updates
Sections with the same header are automatically updated in place:

```python
docPrint('text', 'Status', 'Starting up')
# Later...
docPrint('text', 'Status', 'Running')  # Updates existing section
```

### Multi-file Documentation
```python
# API documentation
docPrintFile("docs/api.md")
docPrint('header', 'REST API', 'Version 2.0')
docPrint('code_block', 'Authentication', auth_example, language='python')

# Separate log file
docPrintFile("logs/errors.log") 
docPrint('alert', 'Database Error', error_details, alert_type='error')

# Back to main docs
docPrintFile("README.md")
docPrint('header', 'Project Overview', project_description)
```

## Configuration

Located in `docprint.config.constants`:

```python
CACHE_FLUSH_INTERVAL = 30        # Auto-flush interval (seconds)
CACHE_FLUSH_COUNT = 1000         # Auto-flush threshold (calls)
DOC_FILE_PREFIX = "DOC.PRINT"    # Default file prefix
DOC_FILE_EXTENSION = ".md"       # Default file extension
DEFAULT_OUTPUT_DIR = "."         # Default output directory
```

## Dependencies

**Core dependencies:**
- `regex>=2025.9.1` - Fast pattern matching
- `xxhash>=3.5.0` - Fast content hashing

**Optional performance dependencies:**
- `ujson>=5.11.0` - Fast JSON operations for GitHub API
- `orjson>=3.11.3` - Fastest JSON operations (when available)

**GitHub integration notes:**
- Zero overhead when GitHub sync is disabled
- Uses standard library urllib when performance packages unavailable
- Fallback JSON handling maintains compatibility

## Thread Safety

DocPrint is fully thread-safe:
- RLock protection for cache operations
- Atomic file writes prevent corruption
- Safe concurrent access to all functions
- Thread-safe file switching

## Production Usage

```python
import logging
from docprint import docPrint, docPrintFile

# Application startup
docPrintFile("logs/application.md")
docPrint('header', 'Application Startup', f'Started at {datetime.now()}')

# During operation (automatic caching and flushing)
def process_data(data):
    docPrint('text', 'Processing Status', f'Processed {len(data)} items')
    
    if errors:
        docPrint('alert', 'Processing Errors', errors, alert_type='error')
    
    # No manual flush needed - auto-flush handles it

# Clean shutdown (optional manual flush)
def shutdown():
    docPrint('text', 'Shutdown', 'Application stopped gracefully')
    flush_cache()  # Ensure final content is written
```

DocPrint is designed for minimal overhead in production environments with intelligent caching that scales with actual content changes, not call frequency.