"""Environment variable definitions for the Barcable SDK."""

BARCABLE_TRACING_ENVIRONMENT = "BARCABLE_TRACING_ENVIRONMENT"
"""
.. envvar:: BARCABLE_TRACING_ENVIRONMENT

The tracing environment. Can be any lowercase alphanumeric string with hyphens and underscores that does not start with 'barcable'.

**Default value:** ``"default"``
"""

BARCABLE_RELEASE = "BARCABLE_RELEASE"
"""
.. envvar:: BARCABLE_RELEASE

Release number/hash of the application to provide analytics grouped by release.
"""

BARCABLE_PUBLIC_KEY = "BARCABLE_PUBLIC_KEY"
"""
.. envvar:: BARCABLE_PUBLIC_KEY

Public API key of the Barcable project.
"""

BARCABLE_SECRET_KEY = "BARCABLE_SECRET_KEY"
"""
.. envvar:: BARCABLE_SECRET_KEY

Secret API key of the Barcable project.
"""

BARCABLE_HOST = "BARCABLE_HOST"
"""
.. envvar:: BARCABLE_HOST

Host of the Barcable API. Can be set via ``BARCABLE_HOST``.

**Default value:** ``"https://cloud.barcable.com"``
"""

BARCABLE_OTEL_TRACES_EXPORT_PATH = "BARCABLE_OTEL_TRACES_EXPORT_PATH"
"""
.. envvar:: BARCABLE_OTEL_TRACES_EXPORT_PATH

URL path on the configured host to export traces to.

**Default value:** ``"/api/public/otel/v1/traces"``
"""

BARCABLE_DEBUG = "BARCABLE_DEBUG"
"""
.. envvar:: BARCABLE_DEBUG

Enables debug mode for more verbose logging.

**Default value:** ``"False"``
"""

BARCABLE_TRACING_ENABLED = "BARCABLE_TRACING_ENABLED"
"""
.. envvar:: BARCABLE_TRACING_ENABLED

Enables or disables the Barcable client. Default is ``True``.
"""

BARCABLE_MEDIA_UPLOAD_THREAD_COUNT = "BARCABLE_MEDIA_UPLOAD_THREAD_COUNT"
"""
.. envvar:: BARCABLE_MEDIA_UPLOAD_THREAD_COUNT

Number of background threads to handle media uploads from trace ingestion.

**Default value:** ``1``
"""

BARCABLE_FLUSH_AT = "BARCABLE_FLUSH_AT"
"""
.. envvar:: BARCABLE_FLUSH_AT

Maximum batch size before a new ingestion batch is sent to the API.

**Default value:** same as OTEL ``OTEL_BSP_MAX_EXPORT_BATCH_SIZE``
"""

BARCABLE_FLUSH_INTERVAL = "BARCABLE_FLUSH_INTERVAL"
"""
.. envvar:: BARCABLE_FLUSH_INTERVAL

Maximum delay in seconds before a new ingestion batch is sent to the API.

**Default value:** same as OTEL ``OTEL_BSP_SCHEDULE_DELAY``
"""

BARCABLE_SAMPLE_RATE = "BARCABLE_SAMPLE_RATE"
"""
.. envvar:: BARCABLE_SAMPLE_RATE

Float between 0 and 1 indicating the sample rate for traces.

**Default value:** ``1.0``
"""

BARCABLE_OBSERVE_DECORATOR_IO_CAPTURE_ENABLED = "BARCABLE_OBSERVE_DECORATOR_IO_CAPTURE_ENABLED"
"""
.. envvar:: BARCABLE_OBSERVE_DECORATOR_IO_CAPTURE_ENABLED

Whether the ``@observe`` decorator captures args/kwargs/return values by default.

**Default value:** ``True``
"""

BARCABLE_MEDIA_UPLOAD_ENABLED = "BARCABLE_MEDIA_UPLOAD_ENABLED"
"""
.. envvar:: BARCABLE_MEDIA_UPLOAD_ENABLED

Controls whether media detection and upload are attempted by the SDK.

**Default value:** ``True``
"""

BARCABLE_TIMEOUT = "BARCABLE_TIMEOUT"
"""
.. envvar:: BARCABLE_TIMEOUT

Timeout for all API requests in seconds.

**Default value:** ``5``
"""

BARCABLE_PROMPT_CACHE_DEFAULT_TTL_SECONDS = "BARCABLE_PROMPT_CACHE_DEFAULT_TTL_SECONDS"
"""
.. envvar:: BARCABLE_PROMPT_CACHE_DEFAULT_TTL_SECONDS

Default time-to-live in seconds for cached prompts.

**Default value:** ``60``
"""
