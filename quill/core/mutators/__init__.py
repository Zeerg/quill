"""
Mutator modules for Quill fuzzer.

This package contains different mutator implementations for transforming prompts
in various ways to test LLM robustness and safety.
"""

from .base import Mutator, mutator, get_mutator, list_mutators
from .typo import TypoMutator
from .refusal_suppression import RefusalSuppressionMutator

# Import any new mutators here

__all__ = [
    "Mutator",
    "mutator",
    "get_mutator",
    "list_mutators",
    "TypoMutator",
    "RefusalSuppressionMutator",
    # Add any new mutator classes here
]
