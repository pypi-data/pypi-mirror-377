from .base import BaseFormatter

class RichContentFormatter(BaseFormatter):
    def format_section(self, section_type, header, content="", line=True, **kwargs):
        formatters = {
            "alert": self._format_alert,
            "collapsible": self._format_collapsible,
            "image": self._format_image,
            "link_collection": self._format_link_collection
        }
        
        formatter = formatters.get(section_type)
        if formatter:
            return formatter(header, content, line, **kwargs)
        return self._format_default(header, content, line)
    
    def _format_alert(self, header, content, line, **kwargs):
        alert_type = kwargs.get('alert_type', 'info')
        result = self._create_header(header)
        
        alert_prefixes = {
            'info': '[INFO]',
            'warning': '[WARNING]',
            'error': '[ERROR]',
            'success': '[SUCCESS]',
            'note': '[NOTE]'
        }
        
        prefix = alert_prefixes.get(alert_type, '[INFO]')
        
        if isinstance(content, list):
            result += f"> **{prefix}**\n>\n"
            for line_content in content:
                result += f"> {line_content}\n"
        else:
            result += f"> **{prefix}**\n>\n> {content}\n"
        
        result += "\n"
        return self._add_line_if_needed(result, line)
    
    def _format_collapsible(self, header, content, line, **kwargs):
        summary = kwargs.get('summary', 'Details')
        result = self._create_header(header)
        
        result += f"<details>\n<summary>{summary}</summary>\n\n"
        
        if isinstance(content, list):
            for item in content:
                result += f"{item}\n\n"
        else:
            result += f"{content}\n\n"
        
        result += "</details>\n\n"
        return self._add_line_if_needed(result, line)
    
    def _format_image(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if isinstance(content, dict):
            url = content.get('url', '')
            alt_text = content.get('alt', 'Image')
            title = content.get('title', '')
            width = content.get('width', '')
            height = content.get('height', '')
            
            img_tag = f"![{alt_text}]({url}"
            if title:
                img_tag += f' "{title}"'
            img_tag += ")"
            
            if width or height:
                img_tag = f'<img src="{url}" alt="{alt_text}"'
                if width:
                    img_tag += f' width="{width}"'
                if height:
                    img_tag += f' height="{height}"'
                if title:
                    img_tag += f' title="{title}"'
                img_tag += ' />'
            
            result += f"{img_tag}\n\n"
        else:
            result += f"![Image]({content})\n\n"
        
        return self._add_line_if_needed(result, line)
    
    def _format_link_collection(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if isinstance(content, list):
            for link in content:
                if isinstance(link, dict):
                    url = link.get('url', '')
                    text = link.get('text', url)
                    description = link.get('description', '')
                    
                    result += f"- [{text}]({url})"
                    if description:
                        result += f" - {description}"
                    result += "\n"
                else:
                    result += f"- {link}\n"
            result += "\n"
        else:
            result += f"{content}\n\n"
        
        return self._add_line_if_needed(result, line)
    
    def _format_default(self, header, content, line):
        result = self._create_header(header)
        return self._add_content_with_line(result, content, line)
    
    def _add_line_if_needed(self, result, line):
        if line:
            return result + "---\n\n"
        return result