import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from qubesync import RequestBuilder, RequestElement, FluentRequestBuilder


class TestRequestBuilder:
    """Test suite for RequestBuilder DSL functionality."""
    
    def test_builds_correct_json_context_manager_style(self):
        """Test the main DSL functionality using context managers."""
        request_id = "asdf1234"
        max_returned = 20
        
        request = RequestBuilder(version="16.0")
        with request as r:
            with r.QBXML() as qbxml:
                with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
                    with msgs.CustomerQueryRq(requestID=request_id, iterator='Start') as query:
                        query.MaxReturned(max_returned)
                        query.IncludeRetElement('ListID')
                        query.IncludeRetElement('Name')
                        query.IncludeRetElement('FullName')
                        query.IncludeRetElement('IsActive')
        
        expected_json = {
            "version": "16.0",
            "request": [
                {"name": "QBXML", "children": [
                    {"name": "QBXMLMsgsRq", "attributes": {"onError": "stopOnError"}, "children": [
                        {
                            "name": "CustomerQueryRq", 
                            "attributes": {"requestID": request_id, "iterator": "Start"}, 
                            "children": [
                                {"name": "MaxReturned", "text": 20},
                                {"name": "IncludeRetElement", "text": "ListID"},
                                {"name": "IncludeRetElement", "text": "Name"},
                                {"name": "IncludeRetElement", "text": "FullName"},
                                {"name": "IncludeRetElement", "text": "IsActive"}
                            ]
                        }
                    ]}
                ]}
            ]
        }
        
        assert request.as_json() == expected_json
    
    def test_builds_correct_json_ruby_style(self):
        """Test building the same structure without context managers."""
        request_id = "asdf1234"
        max_returned = 20
        
        request = RequestBuilder(version="16.0")
        qbxml = request.QBXML()
        msgs = qbxml.QBXMLMsgsRq(onError='stopOnError')
        query = msgs.CustomerQueryRq(requestID=request_id, iterator='Start')
        query.MaxReturned(max_returned)
        query.IncludeRetElement('ListID')
        query.IncludeRetElement('Name')
        query.IncludeRetElement('FullName')
        query.IncludeRetElement('IsActive')
        
        expected_json = {
            "version": "16.0",
            "request": [
                {"name": "QBXML", "children": [
                    {"name": "QBXMLMsgsRq", "attributes": {"onError": "stopOnError"}, "children": [
                        {
                            "name": "CustomerQueryRq", 
                            "attributes": {"requestID": request_id, "iterator": "Start"}, 
                            "children": [
                                {"name": "MaxReturned", "text": 20},
                                {"name": "IncludeRetElement", "text": "ListID"},
                                {"name": "IncludeRetElement", "text": "Name"},
                                {"name": "IncludeRetElement", "text": "FullName"},
                                {"name": "IncludeRetElement", "text": "IsActive"}
                            ]
                        }
                    ]}
                ]}
            ]
        }
        
        assert request.as_json() == expected_json
    
    def test_element_with_only_text(self):
        """Test creating elements with only text content."""
        request = RequestBuilder(version="16.0")
        element = request.TestElement("some text")
        
        expected = {
            "version": "16.0",
            "request": [
                {"name": "TestElement", "text": "some text"}
            ]
        }
        
        assert request.as_json() == expected
    
    def test_element_with_only_attributes(self):
        """Test creating elements with only attributes."""
        request = RequestBuilder(version="16.0")
        element = request.TestElement(attr1="value1", attr2="value2")
        
        expected = {
            "version": "16.0",
            "request": [
                {"name": "TestElement", "attributes": {"attr1": "value1", "attr2": "value2"}}
            ]
        }
        
        assert request.as_json() == expected
    
    def test_element_with_text_and_attributes(self):
        """Test creating elements with both text and attributes."""
        request = RequestBuilder(version="16.0")
        element = request.TestElement("text content", attr1="value1", attr2="value2")
        
        expected = {
            "version": "16.0",
            "request": [
                {"name": "TestElement", "text": "text content", "attributes": {"attr1": "value1", "attr2": "value2"}}
            ]
        }
        
        assert request.as_json() == expected
    
    def test_nested_elements(self):
        """Test creating nested element structures."""
        request = RequestBuilder(version="16.0")
        with request as r:
            with r.Parent(id="parent1") as parent:
                with parent.Child(name="child1") as child:
                    child.GrandChild("grandchild text")
                parent.Child("child2 text", name="child2")
        
        expected = {
            "version": "16.0",
            "request": [
                {"name": "Parent", "attributes": {"id": "parent1"}, "children": [
                    {"name": "Child", "attributes": {"name": "child1"}, "children": [
                        {"name": "GrandChild", "text": "grandchild text"}
                    ]},
                    {"name": "Child", "text": "child2 text", "attributes": {"name": "child2"}}
                ]}
            ]
        }
        
        assert request.as_json() == expected
    
    def test_multiple_root_elements(self):
        """Test creating multiple root elements."""
        request = RequestBuilder(version="16.0")
        request.FirstRoot("first content")
        request.SecondRoot(attr="value")
        with request.ThirdRoot() as third:
            third.Child("child content")
        
        expected = {
            "version": "16.0",
            "request": [
                {"name": "FirstRoot", "text": "first content"},
                {"name": "SecondRoot", "attributes": {"attr": "value"}},
                {"name": "ThirdRoot", "children": [
                    {"name": "Child", "text": "child content"}
                ]}
            ]
        }
        
        assert request.as_json() == expected
    
    def test_python_reserved_words_handling(self):
        """Test handling of Python reserved words using trailing underscore."""
        request = RequestBuilder(version="16.0")
        element = request.TestElement(class_="test-class", for_="test-for", if_="test-if")
        
        expected = {
            "version": "16.0",
            "request": [
                {"name": "TestElement", "attributes": {"class": "test-class", "for": "test-for", "if": "test-if"}}
            ]
        }
        
        assert request.as_json() == expected
    
    def test_as_dict_alias(self):
        """Test that as_dict() is an alias for as_json()."""
        request = RequestBuilder(version="16.0")
        request.TestElement("test")
        
        assert request.as_dict() == request.as_json()
    
    def test_custom_version(self):
        """Test using a custom version."""
        request = RequestBuilder(version="14.0")
        request.TestElement("test")
        
        expected = {
            "version": "14.0",
            "request": [
                {"name": "TestElement", "text": "test"}
            ]
        }
        
        assert request.as_json() == expected
    
    def test_empty_request(self):
        """Test an empty request builder."""
        request = RequestBuilder(version="16.0")
        
        expected = {
            "version": "16.0",
            "request": []
        }
        
        assert request.as_json() == expected


class TestRequestElement:
    """Test suite for RequestElement functionality."""
    
    def test_element_creation(self):
        """Test basic element creation."""
        element = RequestElement("TestElement")
        assert element.name == "TestElement"
        assert element.attributes == {}
        assert element.text is None
        assert element.children == []
        assert element.parent is None
    
    def test_element_with_attributes(self):
        """Test element creation with attributes."""
        element = RequestElement("TestElement", {"attr1": "value1", "attr2": "value2"})
        assert element.attributes == {"attr1": "value1", "attr2": "value2"}
    
    def test_element_with_text(self):
        """Test element creation with text."""
        element = RequestElement("TestElement", text="test content")
        assert element.text == "test content"
    
    def test_element_as_dict_minimal(self):
        """Test element serialization with minimal content."""
        element = RequestElement("TestElement")
        expected = {"name": "TestElement"}
        assert element.as_dict() == expected
    
    def test_element_as_dict_with_attributes(self):
        """Test element serialization with attributes."""
        element = RequestElement("TestElement", {"attr": "value"})
        expected = {"name": "TestElement", "attributes": {"attr": "value"}}
        assert element.as_dict() == expected
    
    def test_element_as_dict_with_text(self):
        """Test element serialization with text."""
        element = RequestElement("TestElement", text="content")
        expected = {"name": "TestElement", "text": "content"}
        assert element.as_dict() == expected
    
    def test_element_as_dict_complete(self):
        """Test element serialization with all properties."""
        parent = RequestElement("Parent")
        child = RequestElement("Child", {"attr": "value"}, "text content", parent)
        parent.children.append(child)
        
        expected = {
            "name": "Parent",
            "children": [
                {
                    "name": "Child",
                    "attributes": {"attr": "value"},
                    "text": "text content"
                }
            ]
        }
        
        assert parent.as_dict() == expected


class TestFluentRequestBuilder:
    """Test suite for FluentRequestBuilder chaining functionality."""
    
    def test_fluent_chaining(self):
        """Test method chaining with the fluent builder."""
        request = FluentRequestBuilder(version="16.0")
        
        # Note: This is a different approach - more chain-like but less Ruby-like than context managers
        request.QBXML().QBXMLMsgsRq(onError='stopOnError').CustomerQueryRq(
            requestID='test123', iterator='Start'
        ).add_children([
            ('MaxReturned', 20),
            ('IncludeRetElement', 'ListID'),
            ('IncludeRetElement', 'Name')
        ])
        
        expected = {
            "version": "16.0",
            "request": [
                {"name": "QBXML", "children": [
                    {"name": "QBXMLMsgsRq", "attributes": {"onError": "stopOnError"}, "children": [
                        {
                            "name": "CustomerQueryRq",
                            "attributes": {"requestID": "test123", "iterator": "Start"},
                            "children": [
                                {"name": "MaxReturned", "text": 20},
                                {"name": "IncludeRetElement", "text": "ListID"},
                                {"name": "IncludeRetElement", "text": "Name"}
                            ]
                        }
                    ]}
                ]}
            ]
        }
        
        assert request.as_json() == expected
    
    def test_add_children_with_dicts(self):
        """Test adding children using dictionary format."""
        request = FluentRequestBuilder(version="16.0")
        request.Root().add_children([
            {'name': 'Child1', 'text': 'text1'},
            {'name': 'Child2', 'attributes': {'attr': 'value'}},
            {'name': 'Child3', 'text': 'text3', 'attributes': {'attr': 'value'}}
        ])
        
        expected = {
            "version": "16.0",
            "request": [
                {"name": "Root", "children": [
                    {"name": "Child1", "text": "text1"},
                    {"name": "Child2", "attributes": {"attr": "value"}},
                    {"name": "Child3", "text": "text3", "attributes": {"attr": "value"}}
                ]}
            ]
        }
        
        assert request.as_json() == expected
    
    def test_add_children_error_handling(self):
        """Test error handling when trying to add children without current element."""
        request = FluentRequestBuilder(version="16.0")
        
        with pytest.raises(ValueError, match="No current element to add children to"):
            request.add_children([('Child', 'text')])


class TestQuubeSyncNamespace:
    """Test suite for namespaced QubeSync classes."""
    
    def test_namespaced_request_builder(self):
        """Test using RequestBuilder directly."""
        request_id = "namespaced_test"
        max_returned = 25
        
        request = RequestBuilder(version="16.0")
        with request as r:
            with r.QBXML() as qbxml:
                with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
                    with msgs.CustomerQueryRq(requestID=request_id, iterator='Start') as query:
                        query.MaxReturned(max_returned)
                        query.IncludeRetElement('ListID')
                        query.IncludeRetElement('Name')
        
        expected_json = {
            "version": "16.0",
            "request": [
                {"name": "QBXML", "children": [
                    {"name": "QBXMLMsgsRq", "attributes": {"onError": "stopOnError"}, "children": [
                        {
                            "name": "CustomerQueryRq", 
                            "attributes": {"requestID": request_id, "iterator": "Start"}, 
                            "children": [
                                {"name": "MaxReturned", "text": 25},
                                {"name": "IncludeRetElement", "text": "ListID"},
                                {"name": "IncludeRetElement", "text": "Name"}
                            ]
                        }
                    ]}
                ]}
            ]
        }
        
        assert request.as_json() == expected_json
    
    def test_namespaced_fluent_builder(self):
        """Test using FluentRequestBuilder directly."""
        request = FluentRequestBuilder(version="16.0")
        request.QBXML().QBXMLMsgsRq(onError='stopOnError').CustomerQueryRq(
            requestID='namespaced_fluent', iterator='Start'
        ).add_children([
            ('MaxReturned', 15),
            ('IncludeRetElement', 'ListID'),
            ('IncludeRetElement', 'FullName')
        ])
        
        expected = {
            "version": "16.0",
            "request": [
                {"name": "QBXML", "children": [
                    {"name": "QBXMLMsgsRq", "attributes": {"onError": "stopOnError"}, "children": [
                        {
                            "name": "CustomerQueryRq",
                            "attributes": {"requestID": "namespaced_fluent", "iterator": "Start"},
                            "children": [
                                {"name": "MaxReturned", "text": 15},
                                {"name": "IncludeRetElement", "text": "ListID"},
                                {"name": "IncludeRetElement", "text": "FullName"}
                            ]
                        }
                    ]}
                ]}
            ]
        }
        
        assert request.as_json() == expected
    
    def test_namespaced_request_element(self):
        """Test using RequestElement directly."""
        element = RequestElement("TestElement", {"attr": "value"}, "test content")
        
        expected = {
            "name": "TestElement",
            "attributes": {"attr": "value"},
            "text": "test content"
        }
        
        assert element.as_dict() == expected


# Ruby-style test that mimics the original RSpec test exactly
class TestRubyStyleEquivalent:
    """Test that exactly mimics the Ruby RSpec test structure."""
    
    def test_builds_the_correct_json(self):
        """Direct translation of the Ruby RSpec test."""
        request_id = "asdf1234"
        max_returned = 20
        
        # Most Ruby-like syntax using context managers
        request = RequestBuilder(version="16.0")
        with request as r:
            with r.QBXML() as qbxml_block:
                with qbxml_block.QBXMLMsgsRq(onError='stopOnError') as msgs_block:
                    with msgs_block.CustomerQueryRq(requestID=request_id, iterator='Start') as query_block:
                        query_block.MaxReturned(max_returned)
                        query_block.IncludeRetElement('ListID')
                        query_block.IncludeRetElement('Name')
                        query_block.IncludeRetElement('FullName')
                        query_block.IncludeRetElement('IsActive')
        
        expected_json = {
            "version": "16.0",
            "request": [
                {"name": "QBXML", "children": [
                    {"name": "QBXMLMsgsRq", "attributes": {"onError": "stopOnError"}, "children": [
                        {
                            "name": "CustomerQueryRq", 
                            "attributes": {"requestID": request_id, "iterator": "Start"}, 
                            "children": [
                                {"name": "MaxReturned", "text": 20},
                                {"name": "IncludeRetElement", "text": "ListID"},
                                {"name": "IncludeRetElement", "text": "Name"},
                                {"name": "IncludeRetElement", "text": "FullName"},
                                {"name": "IncludeRetElement", "text": "IsActive"}
                            ]
                        }
                    ]}
                ]}
            ]
        }
        
        # This is the exact assertion from the Ruby test
        assert request.as_json() == expected_json


if __name__ == "__main__":
    pytest.main([__file__])