from .base import BaseFormatter

class VisualFormatter(BaseFormatter):
    def format_section(self, section_type, header, content="", line=True, **kwargs):
        formatters = {
            "badge": self._format_badge,
            "html_block": self._format_html_block,
            "css_block": self._format_css_block,
            "svg_animation": self._format_svg_animation
        }
        
        formatter = formatters.get(section_type)
        if formatter:
            return formatter(header, content, line, **kwargs)
        return self._format_default(header, content, line)
    
    def _format_badge(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if isinstance(content, dict):
            label = content.get('label', 'badge')
            message = content.get('message', 'info')
            color = content.get('color', 'blue')
            style = content.get('style', 'flat')
            url = content.get('url', '')
            
            badge_url = f"https://img.shields.io/badge/{label}-{message}-{color}?style={style}"
            
            if url:
                result += f"[![{label}]({badge_url})]({url})\n\n"
            else:
                result += f"![{label}]({badge_url})\n\n"
        else:
            result += f"{content}\n\n"
        
        return self._add_line_if_needed(result, line)
    
    def _format_html_block(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if isinstance(content, dict):
            tag = content.get('tag', 'div')
            attrs = content.get('attributes', {})
            inner_content = content.get('content', '')
            
            attr_string = ' '.join([f'{k}="{v}"' for k, v in attrs.items()])
            if attr_string:
                attr_string = ' ' + attr_string
            
            result += f"<{tag}{attr_string}>\n{inner_content}\n</{tag}>\n\n"
        else:
            result += f"{content}\n\n"
        
        return self._add_line_if_needed(result, line)
    
    def _format_css_block(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if isinstance(content, dict):
            selector = content.get('selector', '.default')
            styles = content.get('styles', {})
            
            result += f"```css\n{selector} {{\n"
            for prop, value in styles.items():
                result += f"  {prop}: {value};\n"
            result += "}\n```\n\n"
        else:
            result += f"```css\n{content}\n```\n\n"
        
        return self._add_line_if_needed(result, line)
    
    def _format_svg_animation(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if isinstance(content, dict):
            width = content.get('width', 100)
            height = content.get('height', 100)
            elements = content.get('elements', [])
            
            result += f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n'
            
            for element in elements:
                if isinstance(element, dict):
                    tag = element.get('tag', 'rect')
                    attrs = element.get('attributes', {})
                    animations = element.get('animations', [])
                    
                    attr_string = ' '.join([f'{k}="{v}"' for k, v in attrs.items()])
                    result += f'  <{tag} {attr_string}>\n'
                    
                    for anim in animations:
                        if isinstance(anim, dict):
                            anim_attrs = ' '.join([f'{k}="{v}"' for k, v in anim.items()])
                            result += f'    <animate {anim_attrs} />\n'
                    
                    result += f'  </{tag}>\n'
            
            result += '</svg>\n\n'
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