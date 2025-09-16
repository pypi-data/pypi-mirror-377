import os
from pathlib import Path
from typing import List, Optional, Union
from .parsers import ParserRegistry, Comment
from .rules import RuleRegistry


class CommentRemover:
    """Main class for removing auto-generated comments from code files"""
    
    def __init__(self, rule_registry: Optional[RuleRegistry] = None,
                 parser_registry: Optional[ParserRegistry] = None):
        self.rule_registry = rule_registry or RuleRegistry()
        self.parser_registry = parser_registry or ParserRegistry()
    
    def clean_file(self, file_path: Union[str, Path], 
                   dry_run: bool = False) -> tuple[int, List[str]]:
        """
        Clean a single file by removing auto-generated comments
        
        Args:
            file_path: Path to the file to clean
            dry_run: If True, don't actually modify the file
        
        Returns:
            Tuple of (number of comments removed, list of removed full lines)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix
        parser = self.parser_registry.get_parser(extension)
        
        if not parser:
            return 0, []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            original_content = content
        
        comments = parser.extract_comments(content)
        removed_lines = []
        lines = content.split('\n')
        
        comments_to_remove = []
        for comment in comments:
            if self.rule_registry.should_remove(comment.content):
                comments_to_remove.append(comment)
                # Store the full line(s) that will be removed
                if comment.is_multiline:
                    for line_num in range(comment.start_line, comment.end_line + 1):
                        if line_num < len(lines):
                            removed_lines.append(lines[line_num])
                else:
                    if comment.start_line < len(lines):
                        line = lines[comment.start_line]
                        if parser.single_line and parser.single_line in line:
                            removed_lines.append(line)
        
        if not comments_to_remove:
            return 0, []
        
        comments_to_remove.sort(key=lambda c: c.start_line, reverse=True)
        
        for comment in comments_to_remove:
            if comment.is_multiline:
                lines[comment.start_line:comment.end_line + 1] = []
            else:
                line = lines[comment.start_line]
                if parser.single_line:
                    comment_start = line.find(parser.single_line)
                    if comment_start != -1:
                        new_line = line[:comment_start].rstrip()
                        if new_line:
                            lines[comment.start_line] = new_line
                        else:
                            del lines[comment.start_line]
        
        new_content = '\n'.join(lines)
        
        if not dry_run and new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        return len(comments_to_remove), removed_lines
    
    def clean_directory(self, directory: Union[str, Path], 
                       extensions: Optional[List[str]] = None,
                       recursive: bool = True,
                       dry_run: bool = False) -> dict:
        """
        Clean all files in a directory
        
        Args:
            directory: Directory to clean
            extensions: List of file extensions to process (e.g., ['.py', '.js'])
            recursive: Whether to process subdirectories
            dry_run: If True, don't actually modify files
        
        Returns:
            Dictionary with statistics about the cleaning operation
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory}")
        
        stats = {
            'files_processed': 0,
            'files_modified': 0,
            'comments_removed': 0,
            'errors': []
        }
        
        pattern = '**/*' if recursive else '*'
        
        for file_path in directory.glob(pattern):
            if not file_path.is_file():
                continue
            
            if extensions and file_path.suffix not in extensions:
                continue
            
            if not self.parser_registry.get_parser(file_path.suffix):
                continue
            
            try:
                removed_count, _ = self.clean_file(file_path, dry_run=dry_run)
                stats['files_processed'] += 1
                if removed_count > 0:
                    stats['files_modified'] += 1
                    stats['comments_removed'] += removed_count
            except Exception as e:
                stats['errors'].append({
                    'file': str(file_path),
                    'error': str(e)
                })
        
        return stats