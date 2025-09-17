from pathlib import Path
from typing import List, Dict, Optional, Union

import numpy as np
import pandas as pd


def read_polymer_file(file_path: Union[str, Path]) -> List[np.ndarray]:
    """
    Reads a polymer .dat file and returns a list of NumPy arrays.

    Args:
        file_path: Path to the polymer chain file

    Returns:
        List of NumPy arrays, each representing one polymer chain
    """
    with open(file_path, "r") as file:
        data = file.read().splitlines()

    polymers = [
        np.array([int(num) for num in line.split()]) for line in data if line.strip()
    ]

    return polymers


def create_polymer_array(
    polymers: List[np.ndarray],
    max_length: Optional[int] = None,
    max_polymers: Optional[int] = None,
    pad_value: int = -1,
) -> np.ndarray:
    """
    Creates a 2D NumPy array from polymer chains with padding for variable lengths.

    Args:
        polymers: List of polymer arrays
        max_length: Maximum length to pad to (uses longest polymer if None)
        max_polymers: Maximum number of polymers to include (None for all)
        pad_value: Value to use for padding

    Returns:
        2D array where each row is a polymer chain
    """
    if not polymers:
        return np.array([])

    if max_polymers is not None:
        polymers = polymers[:max_polymers]

    lengths = [len(p) for p in polymers]

    if max_length is None:
        max_length = max(lengths)
    elif max_length == "mean":
        max_length = int(np.ceil(np.mean(lengths)))

    # Create padded array
    result = np.full((len(polymers), max_length), pad_value, dtype=int)

    for i, polymer in enumerate(polymers):
        result[i, : len(polymer)] = polymer[:max_length]

    return result


def create_polymer_dataframe(
    polymers: List[np.ndarray], monomer_mapping: Dict[int, str] = {3: "A", 4: "B"}
) -> pd.DataFrame:
    """
    Creates a DataFrame with polymer statistics and sequences.

    Args:
        polymers: List of polymer arrays
        monomer_mapping: Dictionary mapping monomer IDs to names

    Returns:
        DataFrame with polymer information
    """
    data = []

    for i, polymer in enumerate(polymers):
        # Basic statistics
        length = len(polymer)

        # Count monomer types
        monomer_counts = {}
        for monomer_id, monomer_name in monomer_mapping.items():
            count = np.sum(polymer == monomer_id)
            monomer_counts[f"{monomer_name}_count"] = count
            monomer_counts[f"{monomer_name}_fraction"] = (
                count / length if length > 0 else 0
            )

        # Create row
        row = {
            "polymer_id": i,
            "length": length,
            **monomer_counts,
            "sequence": polymer.tolist(),  # Store the sequence as a list
        }

        data.append(row)

    return pd.DataFrame(data)


def analyze_sequence_runs(
    polymers: List[np.ndarray], target_monomers: List[int] = [3, 4]
) -> pd.DataFrame:
    """
    Analyzes runs of specific monomers in polymer chains.

    Args:
        polymers: List of polymer arrays
        target_monomers: List of monomer IDs to analyze

    Returns:
        DataFrame with run statistics
    """
    run_data = []

    for polymer_id, polymer in enumerate(polymers):
        for monomer_id in target_monomers:
            # Find runs of this monomer
            run_mask = polymer == monomer_id

            # Find run boundaries
            run_starts = np.where(
                np.concatenate(([False], run_mask[:-1] != run_mask[1:], [True]))
            )[0]
            run_lengths = np.diff(run_starts)

            # Only keep runs of the target monomer
            run_types = [
                polymer[start] if start < len(polymer) else -1
                for start in run_starts[:-1]
            ]
            valid_runs = [i for i, t in enumerate(run_types) if t == monomer_id]

            for i in valid_runs:
                run_data.append(
                    {
                        "polymer_id": polymer_id,
                        "monomer_id": monomer_id,
                        "run_start": run_starts[i],
                        "run_length": run_lengths[i],
                        "rel_position": run_starts[i] / len(polymer),
                    }
                )

    return pd.DataFrame(run_data)


def process_polymer_directory(
    directory: Union[str, Path], pattern: str = "poly_*.dat"
) -> Dict[str, List[np.ndarray]]:
    """
    Processes all polymer files in a directory.

    Args:
        directory: Directory containing polymer files
        pattern: Glob pattern to match files

    Returns:
        Dictionary mapping filenames to polymer lists
    """
    directory = Path(directory)
    polymer_data = {}

    for file_path in sorted(directory.glob(pattern)):
        polymers = read_polymer_file(file_path)
        polymer_data[file_path.name] = polymers

    return polymer_data
