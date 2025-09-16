import re
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Comment:
    """Represents a comment in source code"""
    content: str
    start_line: int
    end_line: int
    is_multiline: bool


class LanguageParser:
    """Base class for language-specific comment parsing"""
    
    def __init__(self, single_line: Optional[str] = None, 
                 multi_line_start: Optional[str] = None,
                 multi_line_end: Optional[str] = None):
        self.single_line = single_line
        self.multi_line_start = multi_line_start
        self.multi_line_end = multi_line_end
    
    def extract_comments(self, content: str) -> List[Comment]:
        """Extract all comments from source code"""
        comments = []
        lines = content.split('\n')
        
        if self.single_line:
            comments.extend(self._extract_single_line_comments(lines))
        
        if self.multi_line_start and self.multi_line_end:
            comments.extend(self._extract_multi_line_comments(content, lines))
        
        return comments
    
    def _extract_single_line_comments(self, lines: List[str]) -> List[Comment]:
        """Extract single-line comments"""
        comments = []
        pattern = re.escape(self.single_line)
        
        for i, line in enumerate(lines):
            match = re.search(f'{pattern}(.*)$', line)
            if match:
                comment_text = match.group(1).strip()
                comments.append(Comment(
                    content=comment_text,
                    start_line=i,
                    end_line=i,
                    is_multiline=False
                ))
        
        return comments
    
    def _extract_multi_line_comments(self, content: str, lines: List[str]) -> List[Comment]:
        """Extract multi-line comments"""
        comments = []
        start_pattern = re.escape(self.multi_line_start)
        end_pattern = re.escape(self.multi_line_end)
        
        pattern = f'{start_pattern}(.*?){end_pattern}'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            comment_text = match.group(1).strip()
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = content[:start_pos].count('\n')
            end_line = content[:end_pos].count('\n')
            
            comments.append(Comment(
                content=comment_text,
                start_line=start_line,
                end_line=end_line,
                is_multiline=True
            ))
        
        return comments


class ParserRegistry:
    """Registry for language parsers"""
    
    def __init__(self):
        self.parsers = {}
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """Register default language parsers"""
        
        self.parsers['.py'] = LanguageParser('#', '"""', '"""')
        self.parsers['.pyw'] = self.parsers['.py']
        
        c_style = LanguageParser('//', '/*', '*/')
        for ext in ['.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.cc', 
                    '.h', '.hpp', '.cs', '.go', '.swift', '.kt', '.scala', '.rust',
                    '.rs', '.dart', '.groovy', '.php']:
            self.parsers[ext] = c_style
        
        self.parsers['.rb'] = LanguageParser('#', '=begin', '=end')
        self.parsers['.lua'] = LanguageParser('--', '--[[', ']]')
        self.parsers['.sql'] = LanguageParser('--', '/*', '*/')
        self.parsers['.sh'] = LanguageParser('#')
        self.parsers['.bash'] = LanguageParser('#')
        self.parsers['.ps1'] = LanguageParser('#', '<#', '#>')
        self.parsers['.r'] = LanguageParser('#')
        self.parsers['.m'] = LanguageParser('%')
        self.parsers['.vb'] = LanguageParser("'")
        self.parsers['.pas'] = LanguageParser('//', '{', '}')
        self.parsers['.pl'] = LanguageParser('#', '=pod', '=cut')
        self.parsers['.yaml'] = LanguageParser('#')
        self.parsers['.yml'] = LanguageParser('#')
        self.parsers['.toml'] = LanguageParser('#')
        self.parsers['.ini'] = LanguageParser(';')
        self.parsers['.cfg'] = LanguageParser('#')
        
        html_xml = LanguageParser(None, '<!--', '-->')
        for ext in ['.html', '.htm', '.xml', '.xhtml', '.svg']:
            self.parsers[ext] = html_xml
        
        self.parsers['.css'] = LanguageParser(None, '/*', '*/')
        self.parsers['.scss'] = LanguageParser('//', '/*', '*/')
        self.parsers['.sass'] = LanguageParser('//', '/*', '*/')
        self.parsers['.less'] = LanguageParser('//', '/*', '*/')
    
    def get_parser(self, file_extension: str) -> Optional[LanguageParser]:
        """Get parser for a specific file extension"""
        return self.parsers.get(file_extension.lower())
    
    def register_parser(self, extension: str, parser: LanguageParser):
        """Register a custom parser for a file extension"""
        self.parsers[extension.lower()] = parser