import re

# Regular expression capturing typical refusal responses from LLMs
REFUSAL_RE = re.compile(
    r"""(?:
        # Classic "I'm sorry / apologize ... cannot"
        \bI(?:['’]m)?\s+(?:sorry|apolog(?:ogize|ise)|afraid)\b
        .*?
        \b(?:cannot|can['’]?t|won['’]?t|am\s+unable|refuse|decline)\b

      | # "As an AI language model" style
        \bas\s+an?\s+ai\s+language\s+model\b
        .*?
        \b(?:cannot|can['’]?t|won['’]?t|am\s+unable|refuse|decline)\b

      | # Direct "I cannot / won't / refuse ..." stanza
        \bI\s+(?:cannot|can['’]?t|won['’]?t|am\s+unable|refuse|decline)\b
        .*?
        (?:comply|assist|help|provide|continue|share|disclose|fulfil|fulfill)?

      | # Explicit policy reference
        \bthis\s+request\s+(?:is\s+)?(?:disallowed|violates|against)\b
        .*?
        \bpolicy\b

      | # "According to the policy / rules, I cannot ..."
        \baccording\s+to\s+(?:the\s+)?(?:policy|rules)\b
        .*?
        \bI\s+cannot\b

      | # "I'm afraid I cannot ..." pattern
        \bI['’]?m\s+afraid\b
        .*?
        \b(?:cannot|can['’]?t|won['’]?t|am\s+unable|refuse|decline)\b

      | # "I must decline" short form
        \bI\s+must\s+decline\b
    )""",
    flags=re.IGNORECASE | re.VERBOSE | re.DOTALL,
)

# Simple substring checks for common refusal wording
COMMON_REFUSAL_PHRASES = [
    "as an ai language model",
    "i'm afraid",
    "i am afraid",
    "i must decline",
]


def is_refusal(text: str) -> bool:
    """Return True if `text` looks like an LLM refusal."""
    if not text:
        return False
    lower = text.lower()
    if any(phrase in lower for phrase in COMMON_REFUSAL_PHRASES):
        return True
    return bool(REFUSAL_RE.search(text))
