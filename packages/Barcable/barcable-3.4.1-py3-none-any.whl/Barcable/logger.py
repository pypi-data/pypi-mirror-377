"""Logger configuration for Barcable OpenTelemetry integration.

This module initializes and configures loggers used by the Barcable OpenTelemetry integration.
It sets up the main 'Barcable' logger and configures the httpx logger to reduce noise.

Log levels used throughout Barcable:
- DEBUG: Detailed tracing information useful for development and diagnostics
- INFO: Normal operational information confirming expected behavior
- WARNING: Indication of potential issues that don't prevent operation
- ERROR: Errors that prevent specific operations but allow continued execution
- CRITICAL: Critical errors that may prevent further operation
"""

import logging

# Create the main Barcable logger
Barcable_logger = logging.getLogger("Barcable")
Barcable_logger.setLevel(logging.WARNING)

# Backward compatibility alias (original SDK expected lowercase export)
barcable_logger = Barcable_logger

# Configure httpx logger to reduce noise from HTTP requests
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

# Add console handler if no handlers exist
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
httpx_logger.addHandler(console_handler)
