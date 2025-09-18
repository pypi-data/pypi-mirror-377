from .base import BaseFormatter
from .structural import StructuralFormatter
from .visual import VisualFormatter
from .content_basic import BasicContentFormatter
from .content_rich import RichContentFormatter
from .layout import LayoutFormatter
from .divider import DividerFormatter
from .chart import ChartFormatter

class UnifiedFormatter:
    def __init__(self):
        self.structural = StructuralFormatter()
        self.visual = VisualFormatter()
        self.basic_content = BasicContentFormatter()
        self.rich_content = RichContentFormatter()
        self.layout = LayoutFormatter(self)
        self.divider = DividerFormatter()
        self.chart = ChartFormatter()
    
    def format_section(self, section_type, header, content="", line=True, **kwargs):
        structural_types = {
            "bullets", "horizontal_rule", "code_block", "blockquote",
            "ordered_list", "unordered_list", "footnotes", "definition_list",
            "task_list", "divider"
        }
        
        visual_types = {
            "badge", "html_block", "css_block", "svg_animation"
        }
        
        basic_content_types = {
            "header", "table", "text", "advanced_table"
        }
        
        rich_content_types = {
            "alert", "collapsible", "image", "link_collection"
        }
        
        layout_types = {
            "flex_layout", "table_layout", "grid_layout"
        }
        
        chart_types = {
            "chart"
        }
        
        if section_type in structural_types:
            return self.structural.format_section(section_type, header, content, line, **kwargs)
        elif section_type in visual_types:
            return self.visual.format_section(section_type, header, content, line, **kwargs)
        elif section_type in basic_content_types:
            return self.basic_content.format_section(section_type, header, content, line, **kwargs)
        elif section_type in rich_content_types:
            return self.rich_content.format_section(section_type, header, content, line, **kwargs)
        elif section_type in layout_types:
            return self.layout.format_section(section_type, header, content, line, **kwargs)
        elif section_type in chart_types:
            return self.chart.format_section(section_type, header, content, line, **kwargs)
        else:
            return self.basic_content.format_section("text", header, content, line, **kwargs)