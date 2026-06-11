"""
Deterministic in-memory vector index for ChatIndex retrieval.

Builds embeddings from stored conversation exchanges without provider keys
or external vector databases.
"""

import hashlib
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ctree import MessageNode, TopicNode

DEFAULT_EMBEDDING_DIM = 64
DEFAULT_TOP_K = 5
MAX_TOP_K = 20
PREVIEW_LENGTH = 100


def _stable_bucket(feature: str, dim: int) -> int:
    digest = hashlib.sha256(feature.encode("utf-8")).hexdigest()
    return int(digest, 16) % dim


def deterministic_embed(text: str, dim: int = DEFAULT_EMBEDDING_DIM) -> List[float]:
    """Build a deterministic token/trigram embedding and L2-normalize it."""
    vector = [0.0] * dim
    normalized = " ".join(text.lower().split())

    if not normalized:
        return vector

    features: List[str] = []
    for word in normalized.split():
        features.append(word)
        if len(word) <= 3:
            continue
        features.extend(word[index:index + 3] for index in range(len(word) - 2))

    for feature in features:
        bucket = _stable_bucket(feature, dim)
        vector[bucket] += 1.0

    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude > 0:
        vector = [value / magnitude for value in vector]

    return vector


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    """Return cosine similarity for two equal-length vectors."""
    return sum(a * b for a, b in zip(left, right))


def _preview_text(content: str, max_length: int = PREVIEW_LENGTH) -> str:
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


def _exchange_range(node: MessageNode) -> Tuple[int, int]:
    """Return the conversation message range covered by one exchange."""
    message_count = 2
    if node.system_message:
        message_count += 1
    start_index = node.message_index
    end_index = start_index + message_count
    return start_index, end_index


def _collect_message_nodes(node: Any) -> List[MessageNode]:
    """Depth-first collection of message leaf nodes."""
    if isinstance(node, MessageNode):
        return [node]
    if isinstance(node, TopicNode):
        collected: List[MessageNode] = []
        for child in node.children:
            collected.extend(_collect_message_nodes(child))
        return collected
    return []


@dataclass
class IndexedExchange:
    """One indexed user/assistant exchange."""

    message_index: int
    start_index: int
    end_index: int
    source_text: str
    user_preview: str
    assistant_preview: str
    vector: List[float]


class VectorIndex:
    """In-memory nearest-neighbor index over conversation exchanges."""

    def __init__(self, entries: Optional[List[IndexedExchange]] = None):
        self.entries = list(entries or [])

    @classmethod
    def from_ctree(cls, ctree: Any, dim: int = DEFAULT_EMBEDDING_DIM) -> "VectorIndex":
        """Build an index from all message exchanges in a CTree."""
        entries: List[IndexedExchange] = []
        for node in _collect_message_nodes(ctree.root):
            user_text = node.user_message.get("content", "")
            assistant_text = node.assistant_message.get("content", "")
            source_text = f"{user_text}\n{assistant_text}".strip()
            start_index, end_index = _exchange_range(node)
            entries.append(IndexedExchange(
                message_index=node.message_index,
                start_index=start_index,
                end_index=end_index,
                source_text=source_text,
                user_preview=_preview_text(user_text),
                assistant_preview=_preview_text(assistant_text),
                vector=deterministic_embed(source_text, dim=dim),
            ))

        entries.sort(key=lambda entry: entry.message_index)
        return cls(entries)

    def _bound_top_k(self, top_k: Optional[int]) -> int:
        if top_k is None:
            return DEFAULT_TOP_K

        try:
            requested_top_k = int(top_k)
        except (TypeError, ValueError):
            requested_top_k = DEFAULT_TOP_K

        if requested_top_k < 1:
            return 1
        return min(requested_top_k, MAX_TOP_K, len(self.entries))

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return stable ranked matches with cosine similarity scores."""
        if not self.entries:
            return []

        bounded_top_k = self._bound_top_k(top_k)
        query_vector = deterministic_embed(query)

        ranked = []
        for entry in self.entries:
            score = cosine_similarity(query_vector, entry.vector)
            ranked.append((score, entry))

        ranked.sort(key=lambda item: (-item[0], item[1].message_index))

        results = []
        for score, entry in ranked[:bounded_top_k]:
            results.append({
                "message_index": entry.message_index,
                "score": round(score, 6),
                "text_preview": _preview_text(entry.source_text),
                "user_preview": entry.user_preview,
                "assistant_preview": entry.assistant_preview,
                "start_index": entry.start_index,
                "end_index": entry.end_index,
            })
        return results
