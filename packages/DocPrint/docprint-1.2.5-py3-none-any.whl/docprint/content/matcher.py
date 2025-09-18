try:
    import regex as re
except ImportError:
    import re
from .layout_utils import LayoutUtils

class ContentMatcher:
    def update_or_append(self, existing_content, header, new_content):
        if LayoutUtils.is_layout_content(new_content):
            return self._handle_layout_content(existing_content, header, new_content)
        
        header_pattern = self._create_header_pattern(header)
        match = re.search(header_pattern, existing_content, re.MULTILINE)
        
        if match:
            return self._update_existing_section(existing_content, header, new_content, match)
        else:
            return self._append_new_section(existing_content, new_content)
    
    def _handle_layout_content(self, existing_content, header, new_content):
        normalized_new = LayoutUtils.normalize_layout_content(new_content)
        header_pattern = self._create_header_pattern(header)
        match = re.search(header_pattern, existing_content, re.MULTILINE)
        
        if match:
            start_pos = match.start()
            end_pos = self._find_section_end(existing_content, start_pos)
            existing_section = existing_content[start_pos:end_pos]
            normalized_existing = LayoutUtils.normalize_layout_content(existing_section)
            
            if normalized_existing != normalized_new:
                return (existing_content[:start_pos] + 
                        new_content + 
                        existing_content[end_pos:])
            return existing_content
        else:
            return self._append_new_section(existing_content, new_content)
    
    def _create_header_pattern(self, header):
        escaped_header = re.escape(header)
        return rf'^## {escaped_header}$'
    
    def _update_existing_section(self, existing_content, header, new_content, match):
        start_pos = match.start()
        end_pos = self._find_section_end(existing_content, start_pos)
        existing_section = existing_content[start_pos:end_pos]
        
        if self._content_differs(existing_section, new_content):
            return (existing_content[:start_pos] + 
                    new_content + 
                    existing_content[end_pos:])
        
        return existing_content
    
    def _find_section_end(self, content, start_pos):
        next_header_match = re.search(r'^## ', content[start_pos + 1:], re.MULTILINE)
        
        if next_header_match:
            return start_pos + 1 + next_header_match.start()
        else:
            return len(content)
    
    def _content_differs(self, existing_section, new_content):
        existing_clean = self._clean_content(existing_section)
        new_clean = self._clean_content(new_content)
        return existing_clean != new_clean
    
    def _clean_content(self, content):
        cleaned = content.strip().replace('\r\n', '\n')
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        return cleaned
    
    def _append_new_section(self, existing_content, new_content):
        if existing_content and not existing_content.endswith('\n'):
            return existing_content + '\n' + new_content
        return existing_content + new_content