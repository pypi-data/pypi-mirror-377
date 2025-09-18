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
- Creates single commit per sync with message: `DocPrint: update {filename}`
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
docPrintFile(".")  # Returns to DOC.PRINT.md
docPrintFile("..")  # Returns to DOC.PRINT.md
```

**File switching:**
- Flushes current cache before switching files
- Creates directories automatically
- Thread-safe file operations
- Atomic file writes prevent corruption
- Invalid filename characters are rejected with ValueError

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

#### Advanced Table with Alignment
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
docPrint('blockquote', 'Multi-line Quote', ['Line 1', 'Line 2', 'Line 3'])
```

## Quote

> This is important text

## Multi-line Quote

> Line 1
> Line 2
> Line 3

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

### Layout Elements (Advanced)

#### Flex Layout
```python
docPrint('flex_layout', 'Dashboard', [
    {
        'type': 'text',
        'header': 'CPU Usage',
        'content': '45%',
        'style': 'background: #f0f0f0; padding: 10px;'
    },
    {
        'type': 'table', 
        'header': 'Memory',
        'content': [{'used': '2.1GB', 'free': '1.9GB'}],
        'style': 'background: #e0e0e0; padding: 10px;'
    }
], container_style='display: flex; gap: 20px; margin: 10px;')
```

## Dashboard

<div style="display: flex; gap: 20px; margin: 10px;">

<div style="flex: 1; background: #f0f0f0; padding: 10px;">

### CPU Usage

45%

</div>

<div style="flex: 1; background: #e0e0e0; padding: 10px;">

### Memory

| used | free |
|---|---|
| 2.1GB | 1.9GB |

</div>

</div>

---

#### Table Layout
```python
docPrint('table_layout', 'Comparison View', [
    {
        'type': 'bullets',
        'header': 'Features',
        'content': ['Fast', 'Reliable', 'Scalable'],
        'style': 'border: 1px solid #ccc; padding: 15px;'
    },
    {
        'type': 'alert',
        'header': 'Status',
        'content': 'All systems operational',
        'kwargs': {'alert_type': 'success'},
        'style': 'border: 1px solid #ccc; padding: 15px;'
    }
], table_style='width: 100%; border-collapse: collapse; margin: 10px 0;')
```

## Comparison View

<table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
<tr>
<td style="vertical-align: top; padding: 10px; border: 1px solid #ccc; padding: 15px;">

### Features

- Fast
- Reliable
- Scalable

</td>
<td style="vertical-align: top; padding: 10px; border: 1px solid #ccc; padding: 15px;">

### Status

> **[SUCCESS]**
>
> All systems operational

</td>
</tr>
</table>

---

#### Grid Layout
```python
docPrint('grid_layout', 'Services Overview', [
    {'type': 'text', 'header': 'Web Server', 'content': 'Running'},
    {'type': 'text', 'header': 'Database', 'content': 'Connected'},
    {'type': 'text', 'header': 'Cache', 'content': 'Active'},
    {'type': 'text', 'header': 'Queue', 'content': 'Processing'}
], columns=2, gap='15px')
```

## Services Overview

<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">

<div style="">

### Web Server

Running

</div>

<div style="">

### Database

Connected

</div>

<div style="">

### Cache

Active

</div>

<div style="">

### Queue

Processing

</div>

</div>

---

### Visual Elements

#### Badges
```python
# Without Logo
docPrint('badge', 'Build Status', {
    'label': 'build',
    'message': 'passing',
    'color': 'green',
    'style': 'flat',
    'url': 'https://github.com/repo'
})

# With Logo
docPrint('badge', 'Python Badge', {
    'label': 'Python',
    'message': '3.9+',
    'color': 'blue',
    'logo': 'python',
    'logo_color': 'white',
    'logo_width': '20'
})
```

## Build Status

[![build](https://img.shields.io/badge/build-passing-green?style=flat)](https://github.com/repo)

## Python Badge

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat&logo=python&logoColor=white&logoWidth=20)

---

#### HTML Block
```python
docPrint('html_block', 'Custom HTML', {
    'tag': 'div',
    'attributes': {'class': 'highlight', 'id': 'test-div', 'style': 'background: yellow;'},
    'content': 'This is custom HTML content with styling'
})
```

## Custom HTML

<div class="highlight" id="test-div" style="background: yellow;">
This is custom HTML content with styling
</div>

---

#### CSS Block
```python
docPrint('css_block', 'Component Styling', {
    'selector': '.dashboard-card',
    'styles': {
        'background-color': '#f8f9fa',
        'border': '1px solid #dee2e6',
        'border-radius': '8px',
        'padding': '1rem',
        'margin': '0.5rem'
    }
})
```

## Component Styling

```css
.dashboard-card {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  margin: 0.5rem;
}
```

---

#### SVG Animation
```python
docPrint('svg_animation', 'Loading Spinner', {
    'width': 60,
    'height': 60,
    'elements': [{
        'tag': 'circle',
        'attributes': {
            'cx': 30, 'cy': 30, 'r': 20, 
            'fill': 'none', 'stroke': 'blue', 'stroke-width': 3
        },
        'animations': [{
            'attributeName': 'stroke-dasharray',
            'values': '0 126;63 63;0 126',
            'dur': '2s',
            'repeatCount': 'indefinite'
        }]
    }]
})
```

## Loading Spinner

<svg width="60" height="60" xmlns="http://www.w3.org/2000/svg">
  <circle cx="30" cy="30" r="20" fill="none" stroke="blue" stroke-width="3">
    <animate attributeName="stroke-dasharray" values="0 126;63 63;0 126" dur="2s" repeatCount="indefinite" />
  </circle>
</svg>

---

### Rich Content

#### Alert
```python
docPrint('alert', 'System Warning', 'Disk space running low', alert_type='warning')
docPrint('alert', 'Error Summary', ['Database connection failed', 'Retry attempts exhausted'], alert_type='error')
docPrint('alert', 'Success Message', 'Deployment completed successfully', alert_type='success')
docPrint('alert', 'Information', 'System maintenance scheduled for tonight', alert_type='info')
docPrint('alert', 'Important Note', 'Remember to backup before upgrading', alert_type='note')
```

Alert types: `info`, `warning`, `error`, `success`, `note`

## System Warning

> **[WARNING]**
>
> Disk space running low

## Error Summary

> **[ERROR]**
>
> Database connection failed
> Retry attempts exhausted

---

#### Collapsible Section
```python
docPrint('collapsible', 'Debug Information', [
    'Stack trace: line 42 in main.py',
    'Memory usage: 1.2GB',
    'CPU time: 2.1s'
], summary='Click to show debug details')
```

## Debug Information

<details>
<summary>Click to show debug details</summary>

Stack trace: line 42 in main.py

Memory usage: 1.2GB

CPU time: 2.1s

</details>

---

#### Image
```python
docPrint('image', 'Architecture Diagram', {
    'url': 'https://example.com/architecture.png',
    'alt': 'System Architecture',
    'title': 'Complete system overview',
    'width': '800',
    'height': '400'
})

# Simple version
docPrint('image', 'Screenshot', 'https://example.com/screenshot.jpg')
```

## Architecture Diagram

<img src="https://example.com/architecture.png" alt="System Architecture" width="800" height="400" title="Complete system overview" />

## Screenshot

![Image](https://example.com/screenshot.jpg)

---

#### Link Collection
```python
docPrint('link_collection', 'Development Resources', [
    {'url': 'https://github.com/company/project', 'text': 'Source Code', 'description': 'Main repository'},
    {'url': 'https://docs.company.com', 'text': 'Documentation', 'description': 'API reference'},
    {'url': 'https://company.slack.com', 'text': 'Team Chat'},
    'https://example.com/simple-link'
])
```

## Development Resources

- [Source Code](https://github.com/company/project) - Main repository
- [Documentation](https://docs.company.com) - API reference
- [Team Chat](https://company.slack.com)
- https://example.com/simple-link

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
- `container_style`: CSS styles for layout containers
- `columns`: Number of grid columns (grid_layout)
- `gap`: Grid/flex gap size
- `table_style`: CSS styles for table layouts
- `style`: CSS styles for individual layout blocks

### docPrintFile(filepath)
Set output file for subsequent docPrint calls.

**Parameters:**
- `filepath`: Target file path (creates directories as needed)
- Empty string, ".", or ".." resets to default (DOC.PRINT.md)

**Raises:**
- `ValueError`: Invalid filename characters (< > : " | ? *)

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

## Smart Content Management

### Header Deduplication
DocPrint automatically handles duplicate headers by appending counters:

```python
docPrint('text', 'Status', 'First status')
docPrint('text', 'Status', 'Second status')  # Becomes "Status (1)"
docPrint('text', 'Status', 'Third status')   # Becomes "Status (2)"
```

### Content Updates and Matching
Sections with the same header are automatically updated in place:

```python
docPrint('text', 'Server Status', 'Starting up')
# Later...
docPrint('text', 'Server Status', 'Running')  # Updates existing section
```

### Layout Content Detection
DocPrint automatically detects layout content (flex, grid, table layouts) and uses specialized matching:

```python
# Layout content is normalized before comparison
docPrint('flex_layout', 'Dashboard', layout_data)
# Subsequent calls with same header but different spacing still match correctly
```

## Performance Features

### Smart Caching
- **Content deduplication**: Identical content is automatically deduplicated
- **Hash-based comparison**: Uses xxhash (fast) or MD5 (fallback) for content comparison
- **Layout normalization**: Special handling for HTML layout content
- **Zero redundant I/O**: Repeated identical content doesn't trigger file writes

### Optimized I/O
- **Memory-mapped files**: Large files (>1MB) use mmap for better performance
- **Atomic writes**: Temporary files with atomic replacement prevent corruption
- **Thread-safe operations**: RLock protection for concurrent access
- **Efficient path operations**: Uses pathlib.Path for cross-platform compatibility
- **In-memory content management**: Files loaded once and kept in memory per session

### Auto-flush Behavior
- **Time-based**: Every 30 seconds
- **Count-based**: Every 1000 docPrint calls
- **Only when needed**: Empty cache skips I/O operations
- **Automatic timer**: Starts on first docPrint call

## File Management Deep Dive

### Content Matching Algorithm
DocPrint uses regex-based content matching to update existing sections:

1. **Header Detection**: Searches for `^## {header}$` patterns
2. **Section Boundaries**: Finds next header or end of file
3. **Content Comparison**: Compares cleaned content (normalized whitespace)
4. **Selective Updates**: Only writes when content actually differs

### File Structure
```
## Header 1

Content for section 1

---

## Header 2

Content for section 2

---
```

### Layout Content Handling
Layout formatters (flex_layout, table_layout, grid_layout) receive special treatment:

- Content normalization removes extra whitespace and line breaks
- Hash comparison uses normalized content
- Prevents spurious updates from formatting differences

## Configuration

Located in `docprint.config.constants`:

```python
MAX_FILE_LINES = 5000             # Maximum file lines (unused in current implementation)
CACHE_FLUSH_INTERVAL = 30        # Auto-flush interval (seconds)
CACHE_FLUSH_COUNT = 1000         # Auto-flush threshold (calls)
DOC_FILE_PREFIX = "DOC.PRINT"    # Default file prefix
DOC_FILE_EXTENSION = ".md"       # Default file extension
DEFAULT_OUTPUT_DIR = "."         # Default output directory
DYNAMIC_FILENAME = None          # Reserved for future use
```

## Dependencies

**Core dependencies:**
- `regex>=2025.9.1` - Fast pattern matching (fallback: standard `re`)
- `xxhash>=3.5.0` - Fast content hashing (fallback: `hashlib.md5`)

**Optional performance dependencies:**
- `ujson>=5.11.0` - Fast JSON operations for GitHub API
- `orjson>=3.11.3` - Fastest JSON operations (when available)

**GitHub integration notes:**
- Zero overhead when GitHub sync is disabled
- Uses standard library urllib when performance packages unavailable
- Fallback JSON handling maintains compatibility
- Validates repository access before enabling sync

## Thread Safety

DocPrint is fully thread-safe:
- RLock protection for cache operations and file handling
- Atomic file writes prevent corruption
- Safe concurrent access to all functions
- Thread-safe file switching
- Thread-safe GitHub sync operations

## Production Usage

```python
import logging
from docprint import docPrint, docPrintFile, enableGitCommits

# Application startup
docPrintFile("logs/application.md")

# Enable GitHub sync for production monitoring
enableGitCommits(True, 
                token=os.getenv('GITHUB_TOKEN'), 
                repo="company/production-logs",
                interval_minutes=5)

docPrint('header', 'Application Startup', f'Started at {datetime.now()}')

# During operation (automatic caching and flushing)
def process_data(data):
    docPrint('text', 'Processing Status', f'Processed {len(data)} items')
    
    if errors:
        docPrint('alert', 'Processing Errors', errors, alert_type='error')
    
    # Complex layout for dashboard
    docPrint('flex_layout', 'System Status', [
        {'type': 'text', 'header': 'CPU', 'content': f'{cpu_usage}%'},
        {'type': 'text', 'header': 'Memory', 'content': f'{memory_usage}GB'},
        {'type': 'alert', 'header': 'Alerts', 'content': alert_count, 'kwargs': {'alert_type': 'warning'}}
    ])

# Clean shutdown (optional manual flush)
def shutdown():
    docPrint('text', 'Shutdown', 'Application stopped gracefully')
    flush_cache()  # Ensure final content is written
```

DocPrint is designed for minimal overhead in production environments with intelligent caching that scales with actual content changes, not call frequency.