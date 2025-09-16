"""
RequestBuilder - A Python DSL for building QuickBooks XML requests

This module provides a fluent interface for constructing QBXML requests
in a JSON format for API consumption. QuBeSync API will clean the data of any special 
characters that cause QuickBooks errors and then convert this JSON back into 
QBXML when sending requests to QuickBooks.

Example usage:
    from qubesync import RequestBuilder
    
    request = RequestBuilder(version="16.0") 
    with request as r:
        with r.QBXML() as qbxml:
            with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
                with msgs.CustomerQueryRq(requestID='asdf1234', iterator='Start') as query:
                    query.MaxReturned(20)
                    query.IncludeRetElement('ListID')
                    query.IncludeRetElement('Name')
                    query.IncludeRetElement('FullName')
                    query.IncludeRetElement('IsActive')
    
    json_data = request.as_json()
"""


class RequestElement:
    """Represents a single element in the request structure."""
    
    def __init__(self, name, attributes=None, text=None, parent=None):
        self.name = name
        self.attributes = attributes or {}
        self.text = text
        self.children = []
        self.parent = parent
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def __getattr__(self, name):
        """Create a new child element with the given name."""
        def element_creator(*args, **kwargs):
            # Handle text content as first positional argument
            text = args[0] if args else None
            
            # Convert kwargs to attributes, handling Python reserved words
            attributes = {}
            for key, value in kwargs.items():
                # Convert snake_case to camelCase if needed, but preserve exact case for QB fields
                if key.endswith('_'):
                    key = key[:-1]  # Remove trailing underscore for reserved words
                attributes[key] = value
            
            child = RequestElement(name, attributes, text, self)
            self.children.append(child)
            return child
        
        return element_creator
    
    def as_dict(self):
        """Convert this element to a dictionary representation."""
        result = {"name": self.name}
        
        if self.attributes:
            result["attributes"] = self.attributes
        
        if self.text is not None:
            result["text"] = self.text
        
        if self.children:
            result["children"] = [child.as_dict() for child in self.children]
        
        return result


class RequestBuilder:
    """A fluent interface for building QuickBooks XML requests."""
    
    def __init__(self, version="16.0"):
        self.version = version
        self.root_elements = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def __getattr__(self, name):
        """Create a new root element with the given name."""
        def element_creator(*args, **kwargs):
            # Handle text content as first positional argument
            text = args[0] if args else None
            
            # Convert kwargs to attributes
            attributes = {}
            for key, value in kwargs.items():
                # Handle Python reserved words by removing trailing underscore
                if key.endswith('_'):
                    key = key[:-1]
                attributes[key] = value
            
            element = RequestElement(name, attributes, text)
            self.root_elements.append(element)
            return element
        
        return element_creator
    
    def as_json(self):
        """Convert the request to JSON format."""
        return {
            "version": self.version,
            "request": [element.as_dict() for element in self.root_elements]
        }
    
    def as_dict(self):
        """Alias for as_json() for consistency."""
        return self.as_json()


class FluentRequestBuilder(RequestBuilder):
    """
    Alternative builder with method chaining support for a more Ruby-like feel.
    
    Example:
        request = FluentRequestBuilder(version="16.0")
        request.QBXML().QBXMLMsgsRq(onError='stopOnError').CustomerQueryRq(
            requestID='asdf1234', iterator='Start'
        ).add_children([
            ('MaxReturned', 20),
            ('IncludeRetElement', 'ListID'),
            ('IncludeRetElement', 'Name'),
            ('IncludeRetElement', 'FullName'),
            ('IncludeRetElement', 'IsActive')
        ])
    """
    
    def __init__(self, version="16.0"):
        super().__init__(version)
        self._current_element = None
    
    def __getattr__(self, name):
        """Create a new element and return self for chaining."""
        def element_creator(*args, **kwargs):
            text = args[0] if args else None
            attributes = {k.rstrip('_'): v for k, v in kwargs.items()}
            
            if self._current_element is None:
                # Creating root element
                element = RequestElement(name, attributes, text)
                self.root_elements.append(element)
                self._current_element = element
            else:
                # Creating child element
                element = RequestElement(name, attributes, text, self._current_element)
                self._current_element.children.append(element)
                self._current_element = element
            
            return self
        
        return element_creator
    
    def add_children(self, children_data):
        """Add multiple children to the current element."""
        if self._current_element is None:
            raise ValueError("No current element to add children to")
        
        for child_data in children_data:
            if isinstance(child_data, tuple) and len(child_data) == 2:
                name, text = child_data
                child = RequestElement(name, text=text, parent=self._current_element)
                self._current_element.children.append(child)
            elif isinstance(child_data, dict):
                name = child_data.get('name')
                attributes = child_data.get('attributes', {})
                text = child_data.get('text')
                child = RequestElement(name, attributes, text, self._current_element)
                self._current_element.children.append(child)
        
        return self
    
    def parent(self):
        """Move back to the parent element for continued chaining."""
        if self._current_element and self._current_element.parent:
            self._current_element = self._current_element.parent
        return self
    
    def root(self):
        """Return to the root level."""
        self._current_element = None
        return self
