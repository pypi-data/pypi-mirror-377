# Azure App Insights Logger

A simple logging utility for python application that provides consistent logging setup across different modules using AzureLogHandler. Log will also be streamted to the console.

## Installation

```bash
pip install azappinsights-logger
```
Depdencies `opencensus-ext-azure` and `python-dotenv` should be installed with the package.
## Usage

Create an environment variable with the name `APPLICATIONINSIGHTS_CONNECTION_STRING` and pass the value for app insights connections string.

```python
from azappinsights_logger.logger import setup_logger

# Create a logger with default settings
logger = setup_logger("my.module")

# Create a logger with custom level
logger = setup_logger("my.module", level=logging.DEBUG)

# Use the logger
logger.info("This is an info message")
logger.debug("This is a debug message")
logger.error("This is an error message")
```

## Features

- Consistent logging format across all modules
- Simple setup with sensible defaults
- Customizable log levels and formats
- Thread-safe logging configuration

## License

This project is licensed under the MIT License