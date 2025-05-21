from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class CLIConfig:
    """Command-line interface configuration."""

    mode: str
    outdir: Path
    max_prompts: int
    temperature: float
    mutations: List[str]
    verbose: bool
    url: Optional[str] = None
    model: Optional[str] = None
    corpus: Optional[Path] = None
    seed: Optional[int] = None


@dataclass
class FuzzStats:
    """Statistics for fuzzing run."""

    total: int = 0
    anomalies: int = 0
    refusals: int = 0
    success_rate: float = 0.0

    def compute_metrics(self) -> None:
        """Compute attack success rate."""
        if self.total > 0:
            self.success_rate = self.anomalies / self.total
