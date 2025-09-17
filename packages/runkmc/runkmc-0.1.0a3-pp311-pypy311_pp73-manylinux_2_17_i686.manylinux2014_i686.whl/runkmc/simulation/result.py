from typing import Optional, Dict, Any
from dataclasses import dataclass

import pandas as pd

from .registry import SimulationPaths


@dataclass(frozen=True)
class SimulationResult:

    model_name: str
    params: Dict[str, Any]
    paths: SimulationPaths

    def load_results(self) -> pd.DataFrame:
        """Load the simulation results from the CSV file."""
        return pd.read_csv(self.paths.results_filepath)

    def load_sequence_data(self) -> Optional[pd.DataFrame]:
        """Load the sequence data from the CSV file."""
        if not self.paths.has_sequence_data():
            return None
        return pd.read_csv(self.paths.sequence_filepath)
