"""
Base mutator class and registry functionality.
"""

from __future__ import annotations
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Type

# Registry of mutator implementations
_MUTATOR_REGISTRY: Dict[str, Type["Mutator"]] = {}


def mutator(name: str):
    """Class decorator that adds a Mutator to the global registry."""

    def _wrap(cls: Type["Mutator"]):
        if name in _MUTATOR_REGISTRY:
            raise RuntimeError(f"Duplicate mutator name: {name}")
        _MUTATOR_REGISTRY[name] = cls
        cls.mutator_name = name  # convenience introspection
        return cls

    return _wrap


def get_mutator(name: str) -> "Mutator":
    """
    Get a mutator by name.

    Args:
        name: Name of the mutator to retrieve

    Returns:
        Instantiated mutator instance

    Raises:
        ValueError: If mutator does not exist
    """
    try:
        return _MUTATOR_REGISTRY[name]()
    except KeyError as exc:
        raise ValueError(
            f"Unknown mutator '{name}'. " f"Available: {list(_MUTATOR_REGISTRY)}"
        ) from exc


def list_mutators() -> List[str]:
    """
    Return a list of available mutator names in deterministic (sorted) order.

    Returns:
        List of mutator names
    """
    return sorted(_MUTATOR_REGISTRY)


class Mutator(ABC):
    """
    Base class for all mutators.

    Mutator classes implement strategies for modifying prompts to test
    LLM robustness and safety.

    Sub-classes override `mutate()`. They *should not* hold long-lived state
    so they can be reused safely across threads / processes.
    """

    # Optional friendly label (populated by @mutator decorator)
    mutator_name: str = "<unnamed>"

    # Whether this mutator needs clean text or can follow others (lower=earlier)
    order: int = 100

    @abstractmethod
    def mutate(self, text: str, *, rng: random.Random) -> str:  # pragma: no cover
        """
        Return a mutated prompt string.

        Parameters
        ----------
        text : str
            The input prompt to transform.
        rng  : random.Random
            RNG instance seeded by the Fuzzer so runs are reproducible
            when `--seed` is provided on the CLI.

        Returns
        -------
        str
            The mutated prompt.
        """
        ...

    # Helper so caller can do `mutator_instance(text, rng=rng)`
    def __call__(self, text: str, *, rng: random.Random) -> str:
        """Call the mutator on the given text."""
        return self.mutate(text, rng=rng)

    # Nice repr for logs
    def __repr__(self) -> str:
        """String representation of the mutator."""
        return f"<{self.__class__.__name__}({self.mutator_name})>"
