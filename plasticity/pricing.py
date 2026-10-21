"""Token counts to dollars.

The paper applies "fixed undiscounted input/output prices" to token usage
(Figure 23), so prompt caching discounts are not part of its learning cost.
A table with cache rates gives the billed amount instead, which the run's
spending cap uses.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceTable:
    input_per_mtok: float
    output_per_mtok: float
    cached_input_per_mtok: float | None = None  # cache reads; None: billed as input
    cache_write_per_mtok: float | None = None  # cache writes; None: billed as input
    # (prompt-size threshold, input rate, output rate) for models that charge more for long prompts
    long_context: tuple[int, float, float] | None = None

    def cost(
        self,
        input_tokens: float,
        output_tokens: float,
        cached_input_tokens: float = 0.0,
        cache_write_tokens: float = 0.0,
    ) -> float:
        """USD for one call or one round. `input_tokens` includes the cached and cache-write parts."""
        if min(input_tokens, output_tokens, cached_input_tokens, cache_write_tokens) < 0:
            raise ValueError("token counts must be non-negative")
        if cached_input_tokens + cache_write_tokens > input_tokens:
            raise ValueError("cached and cache-write tokens cannot exceed input_tokens")
        in_rate, out_rate = self.input_per_mtok, self.output_per_mtok
        if self.long_context and input_tokens > self.long_context[0]:
            in_rate, out_rate = self.long_context[1], self.long_context[2]
        read_rate = in_rate if self.cached_input_per_mtok is None else self.cached_input_per_mtok
        write_rate = in_rate if self.cache_write_per_mtok is None else self.cache_write_per_mtok
        fresh = input_tokens - cached_input_tokens - cache_write_tokens
        return (
            fresh * in_rate
            + cached_input_tokens * read_rate
            + cache_write_tokens * write_rate
            + output_tokens * out_rate
        ) / 1e6

    def undiscounted(self) -> "PriceTable":
        """The same model priced the paper's way: every input token at the input rate."""
        return PriceTable(self.input_per_mtok, self.output_per_mtok, long_context=self.long_context)
