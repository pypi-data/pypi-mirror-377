"""
BoostAIO Python Bindings

This package provides Python bindings for the BoostAIO C++ HTTP client library.
"""

import ctypes, os, sys
from enum import IntEnum
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

# Load the shared library
if sys.platform == "darwin":  # macOS
    LIBRARY_NAME = "libhtrio.dylib"
elif sys.platform.startswith("linux"):  # Linux
    LIBRARY_NAME = "libhtrio.so"
else:
    raise RuntimeError(f"Unsupported platform: {sys.platform}")

_LIB_PATH = os.path.join(os.path.dirname(__file__), LIBRARY_NAME)

if not os.path.exists(_LIB_PATH):
    raise FileNotFoundError(f"BoostAIO shared library not found at: {_LIB_PATH}")

_lib = ctypes.CDLL(_LIB_PATH)

class HttpMethod(IntEnum):
    GET = 0
    POST = 1
    PUT = 2
    DELETE = 3
    PATCH = 4
    HEAD = 5
    OPTIONS = 6

class _HttpHeader(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('value', ctypes.c_char_p)
    ]

class _HttpRequest(ctypes.Structure):
    _fields_ = [
        ('method', ctypes.c_int),
        ('url', ctypes.c_char_p),
        ('body', ctypes.c_char_p),
        ('headers', ctypes.POINTER(_HttpHeader)),
        ('header_count', ctypes.c_int)
    ]

class _HttpResponse(ctypes.Structure):
    _fields_ = [
        ('status', ctypes.c_int),
        ('body', ctypes.c_char_p),
        ('headers', ctypes.POINTER(_HttpHeader)),
        ('header_count', ctypes.c_int)
    ]

# Set function signatures
_lib.boostaio_http_get.argtypes = [ctypes.c_char_p, ctypes.POINTER(_HttpResponse)]
_lib.boostaio_http_get.restype = ctypes.c_int

_lib.boostaio_http_post.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(_HttpResponse)]
_lib.boostaio_http_post.restype = ctypes.c_int

_lib.boostaio_http_request.argtypes = [ctypes.POINTER(_HttpRequest), ctypes.POINTER(_HttpResponse)]
_lib.boostaio_http_request.restype = ctypes.c_int

_lib.boostaio_free_response.argtypes = [ctypes.POINTER(_HttpResponse)]
_lib.boostaio_free_response.restype = None

@dataclass
class Response:
    """HTTP Response container"""
    status: int
    body: str
    headers: Dict[str, str]

class HttpClient:
    """BoostAIO HTTP Client wrapper"""
    
    @staticmethod
    def get(url: str, headers: Optional[Dict[str, str]] = None) -> Response:
        """Perform HTTP GET request"""
        return HttpClient.request(HttpMethod.GET, url, headers=headers)

    @staticmethod
    def post(url: str, 
            body: Optional[str] = None, 
            headers: Optional[Dict[str, str]] = None) -> Response:
        """Perform HTTP POST request"""
        return HttpClient.request(HttpMethod.POST, url, body=body, headers=headers)

    @staticmethod
    def put(url: str, 
           body: Optional[str] = None, 
           headers: Optional[Dict[str, str]] = None) -> Response:
        """Perform HTTP PUT request"""
        return HttpClient.request(HttpMethod.PUT, url, body=body, headers=headers)

    @staticmethod
    def delete(url: str, headers: Optional[Dict[str, str]] = None) -> Response:
        """Perform HTTP DELETE request"""
        return HttpClient.request(HttpMethod.DELETE, url, headers=headers)

    @staticmethod
    def request(method: HttpMethod, 
               url: str, 
               body: Optional[str] = None, 
               headers: Optional[Dict[str, str]] = None) -> Response:
        """
        Perform an HTTP request
        
        Args:
            method: HTTP method to use
            url: Target URL
            body: Request body (optional)
            headers: Request headers (optional)
            
        Returns:
            Response object containing status, body and headers
            
        Raises:
            RuntimeError: If the request fails
        """
        req = _HttpRequest()
        req.method = method.value
        req.url = url.encode('utf-8')
        req.body = body.encode('utf-8') if body else None
        
        # Setup headers if provided
        if headers:
            req.header_count = len(headers)
            header_array = (_HttpHeader * len(headers))()
            for i, (name, value) in enumerate(headers.items()):
                header_array[i].name = name.encode('utf-8')
                header_array[i].value = value.encode('utf-8')
            req.headers = header_array
        else:
            req.header_count = 0
            req.headers = None

        resp = _HttpResponse()
        ret = _lib.boostaio_http_request(ctypes.byref(req), ctypes.byref(resp))
        
        if ret != 0:
            _lib.boostaio_free_response(ctypes.byref(resp))
            raise RuntimeError(f"HTTP request failed with code {ret}")

        # Convert response
        result = Response(
            status=resp.status,
            body=resp.body.decode('utf-8') if resp.body else "",
            headers={}
        )
        
        # Extract headers
        if resp.headers and resp.header_count > 0:
            for i in range(resp.header_count):
                name = resp.headers[i].name.decode('utf-8')
                value = resp.headers[i].value.decode('utf-8')
                result.headers[name] = value

        _lib.boostaio_free_response(ctypes.byref(resp))
        return result

# Export public interface
__all__ = ['HttpClient', 'HttpMethod', 'Response']
