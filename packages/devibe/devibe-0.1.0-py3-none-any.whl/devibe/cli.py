import argparse
import sys
from pathlib import Path
from .remover import CommentRemover
from .rules import RuleRegistry, PatternRule


def _get_files_to_process(directory_path, extensions=None, recursive=True):
    """Helper function to get list of files to process"""
    directory_path = Path(directory_path)
    
    if not recursive:
        files = [f for f in directory_path.iterdir() if f.is_file()]
    else:
        files = [f for f in directory_path.rglob('*') if f.is_file()]
    
    if extensions:
        extensions = [ext.lower() for ext in extensions]
        files = [f for f in files if f.suffix.lower() in extensions]
    else:
        # Filter by supported extensions from parser registry
        from .parsers import ParserRegistry
        registry = ParserRegistry()
        supported_extensions = set(registry.parsers.keys())
        files = [f for f in files if f.suffix.lower() in supported_extensions]
    
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(
        description="Remove auto-generated comments from code files",
        prog="devibe"
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        help="File or directory to clean"
    )
    
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process directories recursively"
    )
    
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Show what would be removed without modifying files"
    )
    
    parser.add_argument(
        "-e", "--extensions",
        nargs="+",
        help="File extensions to process (e.g., .py .js .java)"
    )
    
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="List all active rules"
    )
    
    parser.add_argument(
        "--add-pattern",
        metavar=("NAME", "PATTERN"),
        nargs=2,
        action="append",
        help="Add a custom pattern rule"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    remover = CommentRemover()
    
    if args.list_rules:
        print("Active Rules and What They Remove:")
        print("=" * 50)
        
        detailed_rules = remover.rule_registry.get_detailed_rules()
        for rule in detailed_rules:
            print(f"\n{rule['name'].upper()}")
            print(f"Description: {rule['description']}")
            
            if 'patterns' in rule:
                print("Removes comments matching these patterns:")
                for i, pattern in enumerate(rule['patterns'], 1):
                    # Clean up regex patterns for readability
                    readable_pattern = pattern.replace(r'\s+', ' ').replace(r'(?i)', '(case-insensitive) ')
                    readable_pattern = readable_pattern.replace(r'(?:', '').replace(r')', '')
                    readable_pattern = readable_pattern.replace(r'\|', ' OR ')
                    
                    try:
                        print(f"  {i}. {readable_pattern}")
                    except UnicodeEncodeError:
                        # Handle emoji patterns by showing description instead
                        if any(ord(char) > 127 for char in readable_pattern):
                            print(f"  {i}. [Emoji pattern - see source code]")
                        else:
                            safe_pattern = readable_pattern.encode('ascii', 'replace').decode('ascii')
                            print(f"  {i}. {safe_pattern}")
            print("-" * 30)
        
        return 0
    
    if not args.path:
        print("Error: path is required when not using --list-rules", file=sys.stderr)
        return 1
    
    if args.add_pattern:
        for name, pattern in args.add_pattern:
            remover.rule_registry.add_rule(
                PatternRule(name, f"Custom pattern: {pattern}", [pattern])
            )
            if args.verbose:
                print(f"Added custom rule: {name}")
    
    path = Path(args.path)
    
    if not path.exists():
        print(f"Error: Path not found: {path}", file=sys.stderr)
        return 1
    
    try:
        if path.is_file():
            removed, comments = remover.clean_file(path, dry_run=args.dry_run)
            
            if args.dry_run and comments:
                print(f"\n{path} - Would remove {removed} line(s):\n")
                for i, line in enumerate(comments, 1):
                    try:
                        print(f"{i:3}. {line}")
                    except UnicodeEncodeError:
                        # Handle emojis and special characters
                        safe_line = line.encode('ascii', 'replace').decode('ascii')
                        print(f"{i:3}. {safe_line}")
                print()  # Add blank line after
            elif removed > 0:
                action = "Would remove" if args.dry_run else "Removed"
                print(f"{action} {removed} comment(s) from {path}")
            elif args.verbose:
                print(f"No auto-generated comments found in {path}")
        
        else:
            # For directory dry-run, process each file individually to show details
            if args.dry_run:
                print("DRY RUN - Showing what would be removed:\n")
                total_removed = 0
                files_with_changes = 0
                files_processed = 0
                
                for file_path in _get_files_to_process(path, args.extensions, args.recursive):
                    files_processed += 1
                    try:
                        removed, comments = remover.clean_file(file_path, dry_run=True)
                        if removed > 0:
                            files_with_changes += 1
                            total_removed += removed
                            print(f"{file_path} - Would remove {removed} line(s):")
                            for i, line in enumerate(comments, 1):
                                try:
                                    print(f"  {i:2}. {line}")
                                except UnicodeEncodeError:
                                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                                    print(f"  {i:2}. {safe_line}")
                            print()
                    except Exception as e:
                        if args.verbose:
                            print(f"Error processing {file_path}: {e}")
                
                print(f"Summary: {files_processed} files processed, {files_with_changes} would be modified, {total_removed} comments would be removed")
            
            else:
                stats = remover.clean_directory(
                    path,
                    extensions=args.extensions,
                    recursive=args.recursive,
                    dry_run=args.dry_run
                )
                
                print(f"Files processed: {stats['files_processed']}")
                print(f"Files modified: {stats['files_modified']}")
                print(f"Comments removed: {stats['comments_removed']}")
                
                if stats['errors'] and args.verbose:
                    print(f"\nErrors encountered: {len(stats['errors'])}")
                    for error_info in stats['errors']:
                        print(f"  {error_info['file']}: {error_info['error']}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())