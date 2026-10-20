"""Token counts to dollars.

The paper applies "fixed undiscounted input/output prices" to token usage
(Figure 23), so prompt caching discounts are not part of its learning cost.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceTable:
    input_per_mtok: float
    output_per_mtok: float
    cached_input_per_mtok: float | None = None  # None: cached input is billed as input

    def cost(self, input_tokens: float, output_tokens: float, cached_input_tokens: float = 0.0) -> float:
        """USD for one call or one round. `input_tokens` includes the cached part."""
        if min(input_tokens, output_tokens, cached_input_tokens) < 0:
            raise ValueError("token counts must be non-negative")
        if cached_input_tokens > input_tokens:
            raise ValueError("cached_input_tokens cannot exceed input_tokens")
        cached_rate = self.input_per_mtok if self.cached_input_per_mtok is None else self.cached_input_per_mtok
        fresh = input_tokens - cached_input_tokens
        return (
            fresh * self.input_per_mtok
            + cached_input_tokens * cached_rate
            + output_tokens * self.output_per_mtok
        ) / 1e6
