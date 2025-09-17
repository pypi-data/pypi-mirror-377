class BaseFormatter:
    def format_section(self, section_type, header, content="", line=True, **kwargs):
        raise NotImplementedError("Subclasses must implement format_section")
    
    def _create_header(self, header):
        return f"## {header}\n\n"
    
    def _add_content_with_line(self, result, content, line):
        if line and content:
            return result + f"{content}\n\n---\n\n"
        elif content:
            return result + f"{content}\n\n"
        return result
    
    def _ensure_newline_separation(self, result):
        if result and not result.endswith('\n'):
            return result + '\n'
        return result
    
    def _add_line_if_needed(self, result, line):
        if line:
            return result + "---\n\n"
        return result