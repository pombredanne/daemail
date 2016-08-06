# -*- coding: utf-8 -*-
import sys
from   daemail.util import show_argv

def test_show_argv_nothing():
    assert show_argv() == ''

def test_show_argv_empty():
    assert show_argv('') == "''"

def test_show_argv_1simple():
    assert show_argv('foo') == 'foo'

def test_show_argv_2simple():
    assert show_argv('foo', 'bar') == 'foo bar'

def test_show_argv_space():
    assert show_argv('foo bar') == "'foo bar'"

def test_show_argv_backslash():
    assert show_argv('foo\\bar') == r"'foo\bar'"

def test_show_argv_backslash_end():
    assert show_argv('foo\\') == r"'foo\'"

def test_show_argv_apostrophe():
    assert show_argv("foo'bar") == "'foo'\"'\"'bar'"

def test_show_argv_asterisk():
    assert show_argv("foo*bar") == r"'foo*bar'"

def test_show_argv_null():
    assert show_argv("foo\0bar") == r"$'foo\x00bar'"

def test_show_argv_equals():
    assert show_argv("foo=bar") == r"'foo=bar'"

def test_show_argv_2equals():
    assert show_argv("foo=bar", "bar=baz") == r"'foo=bar' 'bar=baz'"

def test_show_argv_2equals_plain():
    assert show_argv("foo=bar", "bar=baz", "quux") == r"'foo=bar' 'bar=baz' quux"

def test_show_argv_equals_plain():
    assert show_argv("foo=bar", "quux") == r"'foo=bar' quux"

def test_show_argv_equals_plain_equals():
    assert show_argv("foo=bar", "quux", "bar=baz") == r"'foo=bar' quux bar=baz"

def test_show_argv_plain_equals():
    assert show_argv("foo", 'bar=baz') == r"foo bar=baz"

def test_show_argv_hyphen():
    assert show_argv("foo-bar") == "foo-bar"

def test_show_argv_underscore():
    assert show_argv("foo_bar") == "foo_bar"

def test_show_argv_colon():
    assert show_argv("foo:bar") == "foo:bar"

def test_show_argv_plus():
    assert show_argv("foo+bar") == "foo+bar"

def test_show_argv_period():
    assert show_argv("foo.bar") == "foo.bar"

def test_show_argv_comma():
    assert show_argv("foo,bar") == "foo,bar"

def test_show_argv_slash():
    assert show_argv("foo/bar") == "foo/bar"

def test_show_argv_exclamation():
    assert show_argv("foo!bar") == "'foo!bar'"

def test_show_argv_quote():
    assert show_argv("foo\"bar") == "'foo\"bar'"

def test_show_argv_hash():
    assert show_argv("foo#bar") == "'foo#bar'"

def test_show_argv_dollar():
    assert show_argv("foo$bar") == "'foo$bar'"

def test_show_argv_percent():
    assert show_argv("foo%bar") == "foo%bar"

def test_show_argv_ampersand():
    assert show_argv("foo&bar") == "'foo&bar'"

def test_show_argv_leftparen():
    assert show_argv("foo(bar") == "'foo(bar'"

def test_show_argv_rightparen():
    assert show_argv("foo)bar") == "'foo)bar'"

def test_show_argv_semicolon():
    assert show_argv("foo;bar") == "'foo;bar'"

def test_show_argv_lessthan():
    assert show_argv("foo<bar") == "'foo<bar'"

def test_show_argv_greaterthan():
    assert show_argv("foo>bar") == "'foo>bar'"

def test_show_argv_question():
    assert show_argv("foo?bar") == "'foo?bar'"

def test_show_argv_at():
    assert show_argv("foo@bar") == "foo@bar"

def test_show_argv_leftbracket():
    assert show_argv("foo[bar") == "'foo[bar'"

def test_show_argv_rightbracket():
    assert show_argv("foo]bar") == "'foo]bar'"

def test_show_argv_caret():
    assert show_argv("foo^bar") == "'foo^bar'"

def test_show_argv_backtick():
    assert show_argv("foo`bar") == "'foo`bar'"

def test_show_argv_leftbrace():
    assert show_argv("foo{bar") == "'foo{bar'"

def test_show_argv_rightbrace():
    assert show_argv("foo}bar") == "'foo}bar'"

def test_show_argv_vbar():
    assert show_argv("foo|bar") == "'foo|bar'"

def test_show_argv_tilde():
    assert show_argv("foo~bar") == "'foo~bar'"

### TODO: Test all escape characters

if sys.version_info[0] >= 3:
    def test_show_argv_surrogateesc():
        assert show_argv('foo\udc80bar') == r"$'foo\x80bar'"

    def test_show_argv_unicode():
        ### TODO: Assumes sys.getfilesystemencoding() == 'utf-8'
        assert show_argv('fooébar') == r"$'foo\xc3\xa9bar'"
