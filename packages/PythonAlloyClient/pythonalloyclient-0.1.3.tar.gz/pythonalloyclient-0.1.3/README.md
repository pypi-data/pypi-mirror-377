# PythonAlloyClient

This is a Python client library for interacting with the [Alloy](https://github.com/AlloyTools/org.alloytools.alloy) Language Server. Currently, it supports checking the syntax of a given Alloy code snippet with the Alloy language server, but more features are planned for the future to make use of the full capabilities of the Alloy language server.

## Installation

You can install the package from PyPI using pip.

```bash
pip install PythonAlloyClient
```

Or install directly from the source.

```bash
git clone https://github.com/mrigankpawagi/PythonAlloyClient.git
cd PythonAlloyClient
pip install -e .
```

## Requirements

- Python 3.6+
- Java Virtual Machine (JVM) 17 or later for running the Alloy language server

## Usage

### Basic Usage

```python
from PythonAlloyClient import AlloyServer

server = AlloyServer() # Initialize the server
server.start() # Start the server

syntax_status = server.check_syntax("sig Person {}")
server.stop() # Stop the server

print(syntax_status.success) # True
```

Once the server is started, you can use the `check_syntax` method to check the syntax of an Alloy code snippet which is supplied as a string. The method returns a `SyntaxStatus` object with the following attributes.

- `success` (`bool`): True if the syntax check passed, False otherwise
- `error_type` (`str`): Type of error (always `Syntax error` for now), None if `success` is True
- `line_number` (`int`): Line number where the error occurred, None if `success` is True
- `column_number` (`int`): Column number where the error occurred, None if `success` is True
- `error_message` (`str`): Error message, None if `success` is True
- `full_error_message` (`str`): Full error message from Alloy, None if `success` is True

If a syntax check failed due to an unexpected error, the `full_error_message` attribute will contain the error message, `success` will be False, and all other attributes will be None.

### Another Example

```python
alloy_code = """
sig X {}
sig A extends X {}
sig A extends X {}
"""
syntax_check = server.check_syntax(alloy_code)

print(syntax_check.success) # False
print(syntax_check.error_type) # Syntax error
print(syntax_check.line_number) # 4
print(syntax_check.column_number) # 5
print(syntax_check.error_message) # "A" is already the name of a sig/parameter in this module.
```

### Custom Alloy Build

By default, PythonAlloyClient uses the JAR file at `PythonAlloyClient/resources/org.alloytools.alloy.dist.jar` to run the Alloy language server. If you want to use a custom build of the Alloy language server, you can specify the path to the JAR file when initializing the `AlloyServer` object.

```python
from PythonAlloyClient import AlloyServer

server = AlloyServer(alloy_jar_path="path/to/alloy.jar")
```

### Other Options

PythonAlloyClient can print logs about the server's status and the requests being made to the server by setting the `quiet` attribute to False. This is set to True by default.

```python
from PythonAlloyClient import AlloyServer

server = AlloyServer(quiet=False)
```

You can also set the `try_get_diagnostics` parameter while checking syntax in order to catch any error-level diagnostics sent by the server. This can be useful for cases where the syntax is correct but there are compilation errors like type-errors. It is set to `False` by default, and has a very minor time overhead. The error returned in this case will have `error_type` as `Diagnostics error`.

```python
from PythonAlloyClient import AlloyServer

server = AlloyServer()
server.start()
syntax_check = server.check_syntax(alloy_code, try_get_diagnostics=True)
```

## Development

### Setting Up the Development Environment

This project uses `pytest` for testing. This is listed in `requirements.txt` and can be installed using pip.

### Running Tests

```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit Pull Requests or issues.
