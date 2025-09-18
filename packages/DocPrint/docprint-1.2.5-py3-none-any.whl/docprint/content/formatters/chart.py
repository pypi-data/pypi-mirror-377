from .base import BaseFormatter

class ChartFormatter(BaseFormatter):
    def format_section(self, section_type, header, content="", line=True, **kwargs):
        if section_type == "chart":
            return self._format_mermaid_chart(header, content, line, **kwargs)
        return self._format_default(header, content, line, **kwargs)
    
    def _format_mermaid_chart(self, header, content, line, **kwargs):
        result = self._create_header(header)
        chart_type = kwargs.get('chart_type', 'pie')
        
        if isinstance(content, dict):
            if chart_type == 'pie':
                return self._format_mermaid_pie(result, content, line, **kwargs)
            elif chart_type == 'flowchart':
                return self._format_mermaid_flowchart(result, content, line, **kwargs)
            elif chart_type == 'timeline':
                return self._format_mermaid_timeline(result, content, line, **kwargs)
            elif chart_type == 'gantt':
                return self._format_mermaid_gantt(result, content, line, **kwargs)
        
        result += f'```mermaid\n{content}\n```\n\n'
        return self._add_line_if_needed(result, line, **kwargs)
    
    def _format_mermaid_pie(self, result, content, line, **kwargs):
        title = content.get('title', 'Pie Chart')
        data = content.get('data', {})
        result += f'```mermaid\npie title {title}\n'
        for label, value in data.items():
            result += f'    "{label}" : {value}\n'
        result += '```\n\n'
        return self._add_line_if_needed(result, line, **kwargs)
    
    def _format_mermaid_flowchart(self, result, content, line, **kwargs):
        result += '```mermaid\ngraph TD\n'
        nodes = content.get('nodes', [])
        edges = content.get('edges', [])

        reserved_words = {"end", "start", "graph", "subgraph"}

        node_id_map = {}

        for node in nodes:
            if isinstance(node, dict):
                original_id = node.get('id', '')
                safe_id = original_id.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')

                if not safe_id or safe_id.lower() in reserved_words or safe_id[0].isdigit():
                    safe_id = f"n_{safe_id or hash(str(node)) % 1000}"

                node_id_map[original_id] = safe_id

                node_label = node.get('label', original_id)
                node_shape = node.get('shape', 'rectangle')

                if node_shape in ['circle', 'round']:
                    result += f'    {safe_id}(("{node_label}"))\n'
                elif node_shape == 'diamond':
                    result += f'    {safe_id}{{{node_label}}}\n'
                else:
                    result += f'    {safe_id}[{node_label}]\n'

        result += '\n'

        for edge in edges:
            if isinstance(edge, dict):
                from_node = node_id_map.get(edge.get('from', ''), '')
                to_node = node_id_map.get(edge.get('to', ''), '')

                if not from_node or not to_node:
                    continue

                edge_label = edge.get('label', '')

                if edge_label:
                    result += f'    {from_node} -->|"{edge_label}"| {to_node}\n'
                else:
                    result += f'    {from_node} --> {to_node}\n'

        result += '```\n\n'
        return self._add_line_if_needed(result, line, **kwargs)

    def _format_mermaid_timeline(self, result, content, line, **kwargs):
        result += '```mermaid\ntimeline\n'
        title = content.get('title', 'Timeline')
        events = content.get('events', [])
        
        result += f'    title {title}\n'
        
        for event in events:
            if isinstance(event, dict):
                period = event.get('period', '2024')
                description = event.get('description', 'Event')
                result += f'        {period} : {description}\n'
        
        result += '```\n\n'
        return self._add_line_if_needed(result, line, **kwargs)
    
    def _format_mermaid_gantt(self, result, content, line, **kwargs):
        title = content.get('title', 'Gantt Chart')
        sections = content.get('sections', [])
        result += '```mermaid\ngantt\n'
        result += f'    title {title}\n'
        result += '    dateFormat YYYY-MM-DD\n'
        
        for section in sections:
            if isinstance(section, dict):
                section_title = section.get('title', 'Section')
                tasks = section.get('tasks', [])
                result += f'    section {section_title}\n'
                for task in tasks:
                    if isinstance(task, dict):
                        task_name = task.get('name', 'Task')
                        task_id = task.get('id', f"task{hash(task_name) % 1000}")
                        start_date = task.get('start', '2024-01-01')
                        duration = task.get('duration', '2d')
                        result += f'    {task_name} :{task_id}, {start_date}, {duration}\n'
        result += '```\n\n'
        return self._add_line_if_needed(result, line, **kwargs)