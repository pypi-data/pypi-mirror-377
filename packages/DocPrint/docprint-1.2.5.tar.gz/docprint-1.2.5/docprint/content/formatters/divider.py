from .base import BaseFormatter

class DividerFormatter(BaseFormatter):
    def format_section(self, section_type, header, content="", line=True, **kwargs):
        if section_type == "divider":
            return self._format_divider(header, content, line, **kwargs)
        return self._format_default(header, content, line, **kwargs)

    def format_divider_line(self, **kwargs):
        divider_type = kwargs.get('divider_type', 'simple')
        color = kwargs.get('color', '#e74c3c')
        thickness = kwargs.get('thickness', 2)
        margin = kwargs.get('margin', '20px 0')

        return self._get_divider_html(divider_type, color, thickness, margin)

    def _format_divider(self, header, content, line, **kwargs):
        no_header = kwargs.get('no_header', False)

        if no_header or not header or header.strip() == "":
            import time
            unique_header = f"divider_{int(time.time() * 1000000) % 1000000}"
            header = unique_header
            skip_header_display = True
        else:
            skip_header_display = False
        
        if skip_header_display:
            result = ""
        else:
            result = self._create_header(header)
        
        divider_html = self.format_divider_line(**kwargs)
        result += divider_html + "\n\n"
        
        if content:
            result += f"{content}\n\n"
        
        return self._add_line_if_needed(result, line, **kwargs)
    
    def _get_divider_html(self, divider_type, color, thickness, margin):
        divider_styles = {
            'simple': self._simple_divider(color, thickness),
            'thick': self._thick_divider(color, thickness),
            'solid': self._solid_divider(color, thickness, margin),
            'gradient': self._gradient_divider(thickness, margin),
            'dotted': self._dotted_divider(color, thickness, margin),
            'shadow': self._shadow_divider(color, thickness),
            'fade': self._fade_divider(color),
            'rainbow': self._rainbow_divider(thickness, margin),
            'dashed': self._dashed_divider(color, thickness, margin),
            'double': self._double_divider(color, thickness, margin)
        }
        
        return divider_styles.get(divider_type, self._simple_divider(color, thickness))
    
    def _simple_divider(self, color, thickness):
        return f'<hr style="border: none; height: {thickness}px; background-color: {color};">'
    
    def _thick_divider(self, color, thickness):
        return f'<hr style="border: none; height: {thickness}px; background-color: {color}; border-radius: 3px;">'
    
    def _solid_divider(self, color, thickness, margin):
        return f'<div style="height: {thickness}px; background-color: {color}; margin: {margin};"></div>'
    
    def _gradient_divider(self, thickness, margin):
        return f'<div style="height: {thickness}px; background: linear-gradient(90deg, #ff6b6b 0%, #4ecdc4 50%, #45b7d1 100%); border-radius: 2px; margin: {margin};"></div>'
    
    def _dotted_divider(self, color, thickness, margin):
        return f'<div style="height: {thickness}px; background: repeating-linear-gradient(90deg, {color} 0px, {color} 10px, transparent 10px, transparent 20px); margin: {margin};"></div>'
    
    def _shadow_divider(self, color, thickness):
        rgba_color = self._hex_to_rgba(color)
        return f'<hr style="border: none; height: {thickness}px; background-color: {color}; box-shadow: 0 2px 4px rgba({rgba_color}, 0.3);">'
    
    def _fade_divider(self, color):
        return f'<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, {color}, transparent);">'
    
    def _rainbow_divider(self, thickness, margin):
        return f'<div style="height: {thickness}px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #f39c12, #e74c3c); border-radius: 10px; margin: {margin};"></div>'
    
    def _dashed_divider(self, color, thickness, margin):
        return f'<div style="height: {thickness}px; background: repeating-linear-gradient(90deg, {color} 0px, {color} 15px, transparent 15px, transparent 30px); margin: {margin};"></div>'
    
    def _double_divider(self, color, thickness, margin):
        single_thickness = max(1, thickness // 3)
        spacing = max(2, thickness // 2)
        return f'<div style="margin: {margin};"><div style="height: {single_thickness}px; background-color: {color}; margin-bottom: {spacing}px;"></div><div style="height: {single_thickness}px; background-color: {color};"></div></div>'
    
    def _hex_to_rgba(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return f"{int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}"
        return "0, 0, 0"