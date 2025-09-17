# BoostAIO

**BoostAIO** is a high-performance, modern HTTP/1.1/2 networking library with native Python bindings. It provides a simple, fast way to perform HTTP requests in Python by leveraging an optimized C++ backend (shipped as a shared library).

---

## Features

- HTTP/1.1 & HTTP/2 support
- Fast, native code (C++ backend via shared library)
- Simple Python API: `import BoostAIO`
- Supports GET, POST, custom methods, custom headers, and more
- Automatic SSL/TLS (https) support

---

## Project Layout

```
BoostAIO/
├── LICENSE
├── README.md
├── BoostAIO/
│   └── __init__.py            # Python API and binding loader
├── src/
│   └── BoostAIO/
│       ├── libhtrio.so        # Compiled C++ shared library (Linux)
│       └── libhtrio.dylib     # Compiled C++ shared library (macOS, optional)
```

---

## Installation

1. **Build/obtain the shared library**  
   Make sure `libhtrio.so` (or `libhtrio.dylib` on macOS) is present in `src/BoostAIO/`.

2. **Install the Python package**  
   You can use this package directly without pip install. Just ensure your working directory structure matches the above and your script points to the right location.

3. **(Optional)**: Add `BoostAIO/` to your `PYTHONPATH` if calling from outside the directory.

---

## Usage Example

```python
from BoostAIO import HttpClient

# Simple GET request
response = HttpClient.get("https://api.github.com/users/octocat")
print("Status:", response.status)
print("Body:", response.body)
print("Headers:", response.headers)

# POST request with custom headers and JSON body
headers = {"Content-Type": "application/json"}
body = '{"name": "test", "description": "test repo"}'
response = HttpClient.post("https://httpbin.org/post", body=body, headers=headers)
print("Status:", response.status)
print("Body:", response.body)

# Custom method (e.g., PATCH)
from BoostAIO import HttpMethod
response = HttpClient.request(
    method=HttpMethod.PATCH,
    url="https://httpbin.org/patch",
    body='{"key": "value"}',
    headers={"Content-Type": "application/json"}
)
print("PATCH Status:", response.status)
print("PATCH Body:", response.body)
```

---

## API

### `HttpClient.get(url: str, headers: dict = None) -> Response`
Perform an HTTP GET request.

### `HttpClient.post(url: str, body: str = None, headers: dict = None) -> Response`
Perform an HTTP POST request.

### `HttpClient.request(method: HttpMethod, url: str, body: str = None, headers: dict = None) -> Response`
Custom HTTP request with any method.

### `Response`
- `.status`: HTTP status code (int)
- `.body`: Response body (str)
- `.headers`: Response headers (dict)

### `HttpMethod`
Enum for HTTP methods (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS, etc.)

---

## How It Works

On import, the BoostAIO Python package will automatically load the C++ shared library (`libhtrio.so`/`libhtrio.dylib`) and expose the HTTP client API using Python classes. No source code or C++ compilation is necessary in the user's project.

---

## License

MIT License (see LICENSE file).

---

## Acknowledgements

- [Boost](https://www.boost.org/) (Asio, Beast)
- [OpenSSL](https://www.openssl.org/)
- Inspired by Python's `requests` and high-performance networking best practices.

---
