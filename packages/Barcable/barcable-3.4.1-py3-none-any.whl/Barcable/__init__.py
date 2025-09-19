""".. include:: ../README.md"""

from Barcable.experiment import Evaluation

from ._client import client as _client_module
from ._client.attributes import BarcableOtelSpanAttributes
from ._client.constants import ObservationTypeLiteral
from ._client.get_client import get_client
from ._client.observe import observe
from ._client.span import (
    BarcableAgent,
    BarcableChain,
    BarcableEmbedding,
    BarcableEvaluator,
    BarcableEvent,
    BarcableGeneration,
    BarcableGuardrail,
    BarcableRetriever,
    BarcableSpan,
    BarcableTool,
)

Barcable = _client_module.Barcable

__all__ = [
    "Barcable",
    "get_client",
    "observe",
    "ObservationTypeLiteral",
    "BarcableSpan",
    "BarcableGeneration",
    "BarcableEvent",
    "BarcableOtelSpanAttributes",
    "BarcableAgent",
    "BarcableTool",
    "BarcableChain",
    "BarcableEmbedding",
    "BarcableEvaluator",
    "BarcableRetriever",
    "BarcableGuardrail",
    "Evaluation",
    "experiment",
    "api",
]
