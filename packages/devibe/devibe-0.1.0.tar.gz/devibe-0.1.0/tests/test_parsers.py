import pytest
from devibe.parsers import ParserRegistry, LanguageParser, Comment


class TestParserRegistry:
    def test_registry_initialization(self):
        registry = ParserRegistry()
        assert len(registry.parsers) > 0
    
    def test_get_parser_for_python(self):
        registry = ParserRegistry()
        parser = registry.get_parser(".py")
        assert parser is not None
        assert isinstance(parser, LanguageParser)
        assert parser.single_line == "#"
    
    def test_get_parser_for_javascript(self):
        registry = ParserRegistry()
        parser = registry.get_parser(".js")
        assert parser is not None
        assert isinstance(parser, LanguageParser)
        assert parser.single_line == "//"
        
        parser_jsx = registry.get_parser(".jsx")
        assert parser_jsx is not None
        assert isinstance(parser_jsx, LanguageParser)
    
    def test_get_parser_for_java(self):
        registry = ParserRegistry()
        parser = registry.get_parser(".java")
        assert parser is not None
        assert isinstance(parser, LanguageParser)
        assert parser.single_line == "//"
    
    def test_get_parser_for_unknown(self):
        registry = ParserRegistry()
        parser = registry.get_parser(".unknown")
        assert parser is None
    
    def test_register_parser(self):
        registry = ParserRegistry()
        
        custom_parser = LanguageParser(single_line=";;")
        registry.register_parser(".custom", custom_parser)
        
        parser = registry.get_parser(".custom")
        assert parser is custom_parser


class TestLanguageParser:
    def test_python_single_line_comments(self):
        parser = LanguageParser(single_line="#")
        code = '''
def foo():
    # This is a comment
    x = 1  # Inline comment
    return x
'''
        comments = parser.extract_comments(code)
        assert len(comments) == 2
        assert any("This is a comment" in c.content for c in comments)
        assert any("Inline comment" in c.content for c in comments)
    
    def test_javascript_single_line_comments(self):
        parser = LanguageParser(single_line="//")
        code = '''
function foo() {
    // This is a comment
    let x = 1; // Inline comment
    return x;
}
'''
        comments = parser.extract_comments(code)
        assert len(comments) == 2
        assert any("This is a comment" in c.content for c in comments)
        assert any("Inline comment" in c.content for c in comments)
    
    def test_javascript_multi_line_comments(self):
        parser = LanguageParser(single_line="//", multi_line_start="/*", multi_line_end="*/")
        code = '''
/*
 * Multi-line comment
 * with multiple lines
 */
function bar() {
    /* Inline block comment */
    return 1;
}
'''
        comments = parser.extract_comments(code)
        assert len(comments) == 2
        assert any("Multi-line comment" in c.content for c in comments)
        assert any("Inline block comment" in c.content for c in comments)
    
    def test_java_comments(self):
        parser = LanguageParser(single_line="//", multi_line_start="/*", multi_line_end="*/")
        code = '''
public class Foo {
    // This is a comment
    int x = 1; // Inline comment
    
    /*
     * Multi-line comment
     */
    public void bar() {
        /* Block comment */
    }
}
'''
        comments = parser.extract_comments(code)
        assert len(comments) >= 4
        assert any("This is a comment" in c.content for c in comments)
        assert any("Inline comment" in c.content for c in comments)
        assert any("Multi-line comment" in c.content for c in comments)
    
    def test_no_comments(self):
        parser = LanguageParser(single_line="#")
        code = '''
def foo():
    x = 1
    y = 2
    return x + y
'''
        comments = parser.extract_comments(code)
        assert len(comments) == 0
    
    def test_comment_object(self):
        comment = Comment(
            content="Test comment",
            start_line=5,
            end_line=5,
            is_multiline=False
        )
        assert comment.content == "Test comment"
        assert comment.start_line == 5
        assert comment.end_line == 5
        assert comment.is_multiline == False