from .base import BaseFormatter

class LayoutFormatter(BaseFormatter):
    def __init__(self, unified_formatter=None):
        self.unified_formatter = unified_formatter
    
    def format_section(self, section_type, header, content="", line=True, **kwargs):
        formatters = {
            "flex_layout": self._format_flex_layout,
            "table_layout": self._format_table_layout,
            "grid_layout": self._format_grid_layout
        }
        
        formatter = formatters.get(section_type)
        if formatter:
            return formatter(header, content, line, **kwargs)
        return self._format_default(header, content, line, **kwargs)
    
    def _format_flex_layout(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if not isinstance(content, list):
            return self._format_default(header, content, line, **kwargs)
        
        container_style = kwargs.get('container_style', 'display: flex; gap: 20px;')
        result += f'<div style="{container_style}">\n\n'
        
        for block in content:
            if not isinstance(block, dict):
                continue
                
            block_type = block.get('type', 'text')
            block_header = block.get('header', '')
            block_content = block.get('content', '')
            block_style = block.get('style', '')
            block_kwargs = block.get('kwargs', {})
            
            div_style = f'flex: 1; {block_style}' if block_style else 'flex: 1;'
            result += f'<div style="{div_style}">\n\n'
            
            formatted_block = self._format_block(block_type, block_header, block_content, **block_kwargs)
            result += formatted_block
            
            result += '\n</div>\n\n'
        
        result += '</div>\n\n'
        return self._add_line_if_needed(result, line, **kwargs)
    
    def _format_table_layout(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if not isinstance(content, list):
            return self._format_default(header, content, line, **kwargs)
        
        table_style = kwargs.get('table_style', 'width: 100%; border-collapse: collapse;')
        result += f'<table style="{table_style}">\n<tr>\n'
        
        for block in content:
            if not isinstance(block, dict):
                continue
                
            block_type = block.get('type', 'text')
            block_header = block.get('header', '')
            block_content = block.get('content', '')
            cell_style = block.get('style', '')
            block_kwargs = block.get('kwargs', {})
            
            td_style = f'vertical-align: top; padding: 10px; {cell_style}' if cell_style else 'vertical-align: top; padding: 10px;'
            result += f'<td style="{td_style}">\n\n'
            
            formatted_block = self._format_block(block_type, block_header, block_content, **block_kwargs)
            result += formatted_block
            
            result += '\n</td>\n'
        
        result += '</tr>\n</table>\n\n'
        return self._add_line_if_needed(result, line, **kwargs)
    
    def _format_grid_layout(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if not isinstance(content, list):
            return self._format_default(header, content, line, **kwargs)
        
        columns = kwargs.get('columns', 2)
        gap = kwargs.get('gap', '20px')
        container_style = f'display: grid; grid-template-columns: repeat({columns}, 1fr); gap: {gap};'
        
        result += f'<div style="{container_style}">\n\n'
        
        for block in content:
            if not isinstance(block, dict):
                continue
                
            block_type = block.get('type', 'text')
            block_header = block.get('header', '')
            block_content = block.get('content', '')
            block_style = block.get('style', '')
            block_kwargs = block.get('kwargs', {})
            
            result += f'<div style="{block_style}">\n\n'
            
            formatted_block = self._format_block(block_type, block_header, block_content, **block_kwargs)
            result += formatted_block
            
            result += '\n</div>\n\n'
        
        result += '</div>\n\n'
        return self._add_line_if_needed(result, line, **kwargs)
    
    def _format_block(self, block_type, block_header, block_content, **kwargs):
        if self.unified_formatter is None:
            raise ValueError("LayoutFormatter requires unified_formatter dependency")
        
        if block_header:
            formatted = self.unified_formatter.format_section(block_type, block_header, block_content, line=False, **kwargs)
            formatted = formatted.replace(f"## {block_header}\n\n", f"### {block_header}\n\n")
            return formatted
        else:
            content_only = self.unified_formatter.format_section(block_type, "temp", block_content, line=False, **kwargs)
            return content_only.replace("## temp\n\n", "", 1)