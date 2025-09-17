import numpy as np


def read_polymer_file(file_path):
    """Read polymer data file and return list of polymer arrays."""
    with open(file_path, "r") as file:
        data = file.read().splitlines()

    polymers = [
        np.array([int(num) for num in line.split()]) for line in data if line.strip()
    ]
    return polymers


def find_sequences(polymer, monomer_id):
    """Find all sequences of specified monomer in a polymer.
    Returns list of (start_pos, length) tuples."""
    # Skip the first element (the 2 value)
    polymer = polymer[1:]
    polymer_length = len(polymer)
    sequences = []

    in_sequence = False
    seq_start = 0

    for i, unit in enumerate(polymer):
        if unit == monomer_id and not in_sequence:
            # Start of new sequence
            seq_start = i
            in_sequence = True
        elif unit != monomer_id and in_sequence:
            # End of sequence
            seq_length = i - seq_start
            sequences.append((seq_start, seq_length))
            in_sequence = False

    # Handle sequence at end of polymer
    if in_sequence:
        seq_length = polymer_length - seq_start
        sequences.append((seq_start, seq_length))

    return sequences


def analyze_sequences_fractional(polymers, monomer_id, num_buckets=10):
    """
    Analyze sequences with fractional assignment to position buckets.

    Returns:
    --------
    bucket_data: list of lists
        Each inner list contains sequence data for that bucket
    """
    bucket_data = [[] for _ in range(num_buckets)]

    for polymer in polymers:
        # Skip the first element (the 2 value)
        effective_polymer = polymer[1:]
        polymer_length = len(effective_polymer)

        if polymer_length == 0:
            continue

        sequences = find_sequences(polymer, monomer_id)

        for start_pos, seq_length in sequences:
            for pos in range(start_pos, start_pos + seq_length):
                # Calculate relative position and corresponding bucket
                rel_pos = pos / polymer_length
                bucket_idx = min(int(rel_pos * num_buckets), num_buckets - 1)

                # Add sequence length to this bucket
                bucket_data[bucket_idx].append(seq_length)

    return bucket_data


def bootstrap_statistics(data, n_bootstrap=1000, confidence=0.95):
    """
    Calculate bootstrap statistics for sequence data.

    Returns:
    --------
    mean, lower_bound, upper_bound
    """
    if len(data) < 2:
        return np.mean(data) if len(data) > 0 else 0, None, None

    # Bootstrap samples
    bootstrap_means = []
    for _ in range(n_bootstrap):
        # Resample with replacement
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_means.append(np.mean(sample))

    # Calculate statistics
    mean = np.mean(data)
    lower_bound = max(1, np.percentile(bootstrap_means, (1 - confidence) * 100 / 2))
    upper_bound = np.percentile(bootstrap_means, 100 - (1 - confidence) * 100 / 2)

    return mean, lower_bound, upper_bound


def geometric_bootstrap(mean_value, sample_size, n_bootstrap=1000, confidence=0.95):
    """
    Bootstrap a geometric distribution with the given mean.

    Returns:
    --------
    lower_bound, upper_bound
    """
    if mean_value <= 1 or sample_size < 2:
        return None, None

    p = 1 / mean_value
    bootstrap_means = []

    for _ in range(n_bootstrap):
        # Generate sample from geometric distribution
        sample = np.random.geometric(p, size=sample_size)
        bootstrap_means.append(np.mean(sample))

    lower_bound = max(1, np.percentile(bootstrap_means, (1 - confidence) * 100 / 2))
    upper_bound = np.percentile(bootstrap_means, 100 - (1 - confidence) * 100 / 2)

    return lower_bound, upper_bound
