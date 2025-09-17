from .base import BaseFormatter

class StructuralFormatter(BaseFormatter):
    def format_section(self, section_type, header, content="", line=True, **kwargs):
        formatters = {
            "bullets": self._format_bullets,
            "horizontal_rule": self._format_horizontal_rule,
            "code_block": self._format_code_block,
            "blockquote": self._format_blockquote,
            "ordered_list": self._format_ordered_list,
            "unordered_list": self._format_unordered_list,
            "footnotes": self._format_footnotes,
            "definition_list": self._format_definition_list,
            "task_list": self._format_task_list
        }

        formatter = formatters.get(section_type)
        if formatter:
            return formatter(header, content, line, **kwargs)
        return self._format_default(header, content, line)

    def _format_bullets(self, header, content, line, **kwargs):
        result = self._create_header(header)
        if isinstance(content, list):
            for item in content:
                result += f"- {item}\n"
            result += "\n"
        else:
            result += f"- {content}\n\n"
        return self._add_line_if_needed(result, line)

    def _format_horizontal_rule(self, header, content, line, **kwargs):
        result = self._create_header(header)
        if content:
            result += f"{content}\n\n"
        result += "---\n\n"
        return result

    def _format_code_block(self, header, content, line, **kwargs):
        language = kwargs.get('language', '')
        result = self._create_header(header)
        result += f"```{language}\n{content}\n```\n\n"
        return self._add_line_if_needed(result, line)

    def _format_blockquote(self, header, content, line, **kwargs):
        result = self._create_header(header)
        if isinstance(content, list):
            for quote_line in content:
                result += f"> {quote_line}\n"
        else:
            lines = str(content).split('\n')
            for quote_line in lines:
                result += f"> {quote_line}\n"
        result += "\n"
        return self._add_line_if_needed(result, line)

    def _format_ordered_list(self, header, content, line, **kwargs):
        result = self._create_header(header)
        if isinstance(content, list):
            for i, item in enumerate(content, 1):
                result += f"{i}. {item}\n"
            result += "\n"
        else:
            result += f"1. {content}\n\n"
        return self._add_line_if_needed(result, line)

    def _format_unordered_list(self, header, content, line, **kwargs):
        result = self._create_header(header)
        if isinstance(content, list):
            for item in content:
                result += f"- {item}\n"
            result += "\n"
        else:
            result += f"- {content}\n\n"
        return self._add_line_if_needed(result, line)

    def _format_default(self, header, content, line):
        result = self._create_header(header)
        return self._add_content_with_line(result, content, line)

    def _format_footnotes(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if isinstance(content, tuple) and len(content) == 2:
            main_text, footnotes = content
            definitions = []
            
            for num, note_content in footnotes.items():
                main_text += f"[^{num}]"
                definitions.append(f"[^{num}]: {note_content}")
            
            result += main_text + "\n\n"
            result += "\n".join(definitions) + "\n\n"
        else:
            result += f"{content}\n\n"
        
        return self._add_line_if_needed(result, line)

    def _format_definition_list(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if isinstance(content, dict):
            for term, definition in content.items():
                result += f"{term}\n: {definition}\n\n"
        else:
            result += f"{content}\n\n"
        
        return self._add_line_if_needed(result, line)

    def _format_task_list(self, header, content, line, **kwargs):
        result = self._create_header(header)
        
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    status = "[x]" if item.get('completed', False) else "[ ]"
                    result += f"- {status} {item.get('task', '')}\n"
                else:
                    result += f"- {item}\n"
            result += "\n"
        else:
            result += f"{content}\n\n"
        
        return self._add_line_if_needed(result, line)