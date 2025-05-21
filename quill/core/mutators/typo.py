"""
Typo mutator implementation.
"""

import random
from .base import Mutator, mutator


@mutator("typo")
class TypoMutator(Mutator):
    """
    Random single-character typo mutation.

    Applies simple character-level mutations like:
    - Transposing adjacent characters
    - Inserting random letters
    - Deleting characters

    This can bypass basic jailbreakers and other simple filters.
    """

    def mutate(self, text: str, *, rng: random.Random) -> str:
        """
        Apply a random typo to the given text.

        Args:
            text: The text to mutate
            rng: Random number generator instance

        Returns:
            Mutated text with a typo
        """
        if not text:
            return text

        action = rng.choice(["transpose", "insert", "delete"])
        idx = rng.randrange(len(text))

        if action == "transpose" and len(text) > 1:
            j = idx + 1 if idx < len(text) - 1 else idx - 1
            chars = list(text)
            chars[idx], chars[j] = chars[j], chars[idx]
            return "".join(chars)

        if action == "insert":
            char = rng.choice("abcdefghijklmnopqrstuvwxyz")
            return text[:idx] + char + text[idx:]

        if action == "delete":
            return text[:idx] + text[idx + 1 :]

        return text  # fallback (rare edge cases)
