"""Span attribute management for Barcable OpenTelemetry integration.

This module defines constants and functions for managing OpenTelemetry span attributes
used by Barcable. It provides a structured approach to creating and manipulating
attributes for different span types (trace, span, generation) while ensuring consistency.

The module includes:
- Attribute name constants organized by category
- Functions to create attribute dictionaries for different entity types
- Utilities for serializing and processing attribute values
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from Barcable._client.constants import (
    ObservationTypeGenerationLike,
    ObservationTypeSpanLike,
)

from Barcable._utils.serializer import EventSerializer
from Barcable.model import PromptClient
from Barcable.types import MapValue, SpanLevel


class BarcableOtelSpanAttributes:
    # Barcable-Trace attributes
    TRACE_NAME = "barcable.trace.name"
    TRACE_USER_ID = "user.id"
    TRACE_SESSION_ID = "session.id"
    TRACE_TAGS = "barcable.trace.tags"
    TRACE_PUBLIC = "barcable.trace.public"
    TRACE_METADATA = "barcable.trace.metadata"
    TRACE_INPUT = "barcable.trace.input"
    TRACE_OUTPUT = "barcable.trace.output"

    # Barcable-observation attributes
    OBSERVATION_TYPE = "barcable.observation.type"
    OBSERVATION_METADATA = "barcable.observation.metadata"
    OBSERVATION_LEVEL = "barcable.observation.level"
    OBSERVATION_STATUS_MESSAGE = "barcable.observation.status_message"
    OBSERVATION_INPUT = "barcable.observation.input"
    OBSERVATION_OUTPUT = "barcable.observation.output"

    # Barcable-observation of type Generation attributes
    OBSERVATION_COMPLETION_START_TIME = "barcable.observation.completion_start_time"
    OBSERVATION_MODEL = "barcable.observation.model.name"
    OBSERVATION_MODEL_PARAMETERS = "barcable.observation.model.parameters"
    OBSERVATION_USAGE_DETAILS = "barcable.observation.usage_details"
    OBSERVATION_COST_DETAILS = "barcable.observation.cost_details"
    OBSERVATION_PROMPT_NAME = "barcable.observation.prompt.name"
    OBSERVATION_PROMPT_VERSION = "barcable.observation.prompt.version"

    # General
    ENVIRONMENT = "barcable.environment"
    RELEASE = "barcable.release"
    VERSION = "barcable.version"

    # Internal
    AS_ROOT = "barcable.internal.as_root"


def create_trace_attributes(
    *,
    name: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    version: Optional[str] = None,
    release: Optional[str] = None,
    input: Optional[Any] = None,
    output: Optional[Any] = None,
    metadata: Optional[Any] = None,
    tags: Optional[List[str]] = None,
    public: Optional[bool] = None,
) -> dict:
    attributes = {
        BarcableOtelSpanAttributes.TRACE_NAME: name,
        BarcableOtelSpanAttributes.TRACE_USER_ID: user_id,
        BarcableOtelSpanAttributes.TRACE_SESSION_ID: session_id,
        BarcableOtelSpanAttributes.VERSION: version,
        BarcableOtelSpanAttributes.RELEASE: release,
        BarcableOtelSpanAttributes.TRACE_INPUT: _serialize(input),
        BarcableOtelSpanAttributes.TRACE_OUTPUT: _serialize(output),
        BarcableOtelSpanAttributes.TRACE_TAGS: tags,
        BarcableOtelSpanAttributes.TRACE_PUBLIC: public,
        **_flatten_and_serialize_metadata(metadata, "trace"),
    }

    return {k: v for k, v in attributes.items() if v is not None}


def create_span_attributes(
    *,
    metadata: Optional[Any] = None,
    input: Optional[Any] = None,
    output: Optional[Any] = None,
    level: Optional[SpanLevel] = None,
    status_message: Optional[str] = None,
    version: Optional[str] = None,
    observation_type: Optional[
        Union[ObservationTypeSpanLike, Literal["event"]]
    ] = "span",
) -> dict:
    attributes = {
        BarcableOtelSpanAttributes.OBSERVATION_TYPE: observation_type,
        BarcableOtelSpanAttributes.OBSERVATION_LEVEL: level,
        BarcableOtelSpanAttributes.OBSERVATION_STATUS_MESSAGE: status_message,
        BarcableOtelSpanAttributes.VERSION: version,
        BarcableOtelSpanAttributes.OBSERVATION_INPUT: _serialize(input),
        BarcableOtelSpanAttributes.OBSERVATION_OUTPUT: _serialize(output),
        **_flatten_and_serialize_metadata(metadata, "observation"),
    }

    return {k: v for k, v in attributes.items() if v is not None}


def create_generation_attributes(
    *,
    name: Optional[str] = None,
    completion_start_time: Optional[datetime] = None,
    metadata: Optional[Any] = None,
    level: Optional[SpanLevel] = None,
    status_message: Optional[str] = None,
    version: Optional[str] = None,
    model: Optional[str] = None,
    model_parameters: Optional[Dict[str, MapValue]] = None,
    input: Optional[Any] = None,
    output: Optional[Any] = None,
    usage_details: Optional[Dict[str, int]] = None,
    cost_details: Optional[Dict[str, float]] = None,
    prompt: Optional[PromptClient] = None,
    observation_type: Optional[ObservationTypeGenerationLike] = "generation",
) -> dict:
    attributes = {
        BarcableOtelSpanAttributes.OBSERVATION_TYPE: observation_type,
        BarcableOtelSpanAttributes.OBSERVATION_LEVEL: level,
        BarcableOtelSpanAttributes.OBSERVATION_STATUS_MESSAGE: status_message,
        BarcableOtelSpanAttributes.VERSION: version,
        BarcableOtelSpanAttributes.OBSERVATION_INPUT: _serialize(input),
        BarcableOtelSpanAttributes.OBSERVATION_OUTPUT: _serialize(output),
        BarcableOtelSpanAttributes.OBSERVATION_MODEL: model,
        BarcableOtelSpanAttributes.OBSERVATION_PROMPT_NAME: prompt.name
        if prompt and not prompt.is_fallback
        else None,
        BarcableOtelSpanAttributes.OBSERVATION_PROMPT_VERSION: prompt.version
        if prompt and not prompt.is_fallback
        else None,
        BarcableOtelSpanAttributes.OBSERVATION_USAGE_DETAILS: _serialize(usage_details),
        BarcableOtelSpanAttributes.OBSERVATION_COST_DETAILS: _serialize(cost_details),
        BarcableOtelSpanAttributes.OBSERVATION_COMPLETION_START_TIME: _serialize(
            completion_start_time
        ),
        BarcableOtelSpanAttributes.OBSERVATION_MODEL_PARAMETERS: _serialize(
            model_parameters
        ),
        **_flatten_and_serialize_metadata(metadata, "observation"),
    }

    return {k: v for k, v in attributes.items() if v is not None}


def _serialize(obj: Any) -> Optional[str]:
    if obj is None or isinstance(obj, str):
        return obj

    return json.dumps(obj, cls=EventSerializer)


def _flatten_and_serialize_metadata(
    metadata: Any, type: Literal["observation", "trace"]
) -> dict:
    prefix = (
        BarcableOtelSpanAttributes.OBSERVATION_METADATA
        if type == "observation"
        else BarcableOtelSpanAttributes.TRACE_METADATA
    )

    metadata_attributes: Dict[str, Union[str, int, None]] = {}

    if not isinstance(metadata, dict):
        metadata_attributes[prefix] = _serialize(metadata)
    else:
        for key, value in metadata.items():
            metadata_attributes[f"{prefix}.{key}"] = (
                value
                if isinstance(value, str) or isinstance(value, int)
                else _serialize(value)
            )

    return metadata_attributes
