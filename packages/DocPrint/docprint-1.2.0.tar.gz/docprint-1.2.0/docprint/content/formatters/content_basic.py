from .base import BaseFormatter

class BasicContentFormatter(BaseFormatter):
    def format_section(self, section_type, header, content="", line=True, **kwargs):
        formatters = {
            "header": self._format_header,
            "table": self._format_table,
            "text": self._format_text,
            "advanced_table": self._format_advanced_table
        }

        formatter = formatters.get(section_type)
        if formatter:
            return formatter(header, content, line, **kwargs)
        return self._format_text(header, content, line)

    def _format_header(self, header, content, line):
        header_line = f"## {header}\n\n"
        if line and content:
            header_line += f"{content}\n\n"
        elif content:
            header_line += f"{content}\n\n"
        return header_line

    def _format_table(self, header, content, line, **kwargs):
        result = f"## {header}\n\n"
        if isinstance(content, list) and len(content) > 0:
            if isinstance(content[0], dict):
                headers = list(content[0].keys())
                result += "| " + " | ".join(headers) + " |\n"
                result += "|" + "---|" * len(headers) + "\n"
                for row in content:
                    values = [str(row.get(h, "")) for h in headers]
                    result += "| " + " | ".join(values) + " |\n"
            else:
                result += str(content) + "\n"
        else:
            result += str(content) + "\n"
        return result + "\n"

    def _format_text(self, header, content, line):
        result = f"## {header}\n\n"
        if line:
            result += f"{content}\n\n---\n\n"
        else:
            result += f"{content}\n\n"
        return result

    def _format_advanced_table(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if isinstance(content, dict) and 'rows' in content:
            headers = content.get('headers', [])
            rows = content.get('rows', [])
            alignment = content.get('alignment', [])
            
            if headers:
                result += "| " + " | ".join(headers) + " |\n"
                
                if alignment:
                    align_chars = []
                    for align in alignment:
                        if align == 'center': 
                            align_chars.append(':---:')
                        elif align == 'right': 
                            align_chars.append('---:')
                        else: 
                            align_chars.append('---')
                    result += "|" + "|".join(align_chars) + "|\n"
                else:
                    result += "|" + " --- |" * len(headers) + "\n"
                
                for row in rows:
                    result += "| " + " | ".join(str(cell) for cell in row) + " |\n"
            result += "\n"
        else:
            return self._format_table(header, content, line, **kwargs)
        
        return self._add_line_if_needed(result, line)