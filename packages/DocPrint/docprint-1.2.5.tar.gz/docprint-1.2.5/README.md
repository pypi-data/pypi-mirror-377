# DocPrint

Runtime documentation generation tool that creates live markdown output with intelligent caching, content deduplication, and optional GitHub integration.

## Installation

```bash
pip install docprint
```

**Performance dependencies (recommended):**
```bash
pip install docprint[performance]
```

## Quick Start

```python
from docprint import docPrint, docFlush, docPrintFile, enableGitCommits

# Basic usage - writes to DOC.PRINT.md
docPrint('text', 'Status', 'Application started')
docPrint('table', 'Metrics', [{'cpu': '45%', 'memory': '2.1GB'}])

# Custom output file
docPrintFile("logs/app.md")
docPrint('header', 'System Status', 'All services operational')

# Force write cached content
docFlush()
```

## GitHub Integration

Automatically sync documentation changes to GitHub:

```python
import os

# Enable auto-sync (requires personal access token)
enableGitCommits(True, 
                token=os.getenv('GITHUB_TOKEN'), 
                repo="username/repository")

# Custom sync interval (default: 1 minute)
enableGitCommits(True, 
                token=token, 
                repo="user/repo", 
                interval_minutes=5)
```

**Setup requirements:**
- GitHub personal access token with repo permissions
- Target repository must exist and be accessible
- Respects API rate limits

## File Management

```python
# Default output
docPrint('text', 'Status', 'Running')  # → DOC.PRINT.md

# Custom files
docPrintFile("reports/daily.md")
docPrint('text', 'Report', 'Daily metrics')  # → reports/daily.md

# Reset to default
docPrintFile("")  # → DOC.PRINT.md
```

Creates directories automatically. Thread-safe operations with atomic file writes.

## Available Formatters

**Basic content:** text, header, table, bullets, code_block

**Structure:** horizontal_rule, blockquote, ordered_list, unordered_list, footnotes, divider

**Layout:** flex_layout, table_layout, grid_layout

**Visual:** badge, html_block, css_block, svg_animation

**Rich content:** alert, collapsible, image, link_collection

See [Formats.md](https://github.com/Varietyz/DocPrint/blob/main/Formats.md) for complete examples. 

## Smart Features

**Content deduplication:** Identical content automatically deduplicated

**Header management:** Duplicate headers get counters (Status, Status (1), Status (2))

**Content updates:** Same headers update existing sections in place

**Auto-flush:** Every 30 seconds or 1000 calls

## Performance

- Hash-based content comparison (xxhash/MD5)
- Memory-mapped files for large documents
- Layout content normalization
- Zero redundant I/O operations
- Thread-safe concurrent access

## Production Example

```python
import os
from docprint import docPrint, docPrintFile, enableGitCommits

# Application setup
docPrintFile("logs/production.md")
enableGitCommits(True, 
                token=os.getenv('GITHUB_TOKEN'), 
                repo="company/logs")

# Runtime logging
docPrint('header', 'Application Startup', f'Started at {datetime.now()}')

def process_batch(data):
    docPrint('text', 'Processing', f'Batch size: {len(data)}')
    
    if errors:
        docPrint('alert', 'Errors', error_list, alert_type='error')
    
    # Dashboard layout
    docPrint('flex_layout', 'System Status', [
        {'type': 'text', 'header': 'CPU', 'content': f'{cpu}%'},
        {'type': 'text', 'header': 'Memory', 'content': f'{mem}GB'}
    ])
```

## Documentation

- [Reference_Table.md](https://github.com/Varietyz/DocPrint/blob/main/Reference_Table.md) - Function signatures and parameters
- [Formats.md](https://github.com/Varietyz/DocPrint/blob/main/Formats.md) - Complete formatter documentation with examples

## Thread Safety

All operations are thread-safe with RLock protection for cache operations and atomic file writes.
