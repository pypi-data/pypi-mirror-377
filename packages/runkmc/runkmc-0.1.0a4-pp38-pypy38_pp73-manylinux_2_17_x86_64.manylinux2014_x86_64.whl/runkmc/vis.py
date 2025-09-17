import numpy as np
import matplotlib.pyplot as plt

from runkmc.analysis.utils import (
    analyze_sequences_fractional,
    bootstrap_statistics,
    geometric_bootstrap,
    find_sequences,
    read_polymer_file,
)


def plot_sequence_distribution(polymers, monomer_id=3, normalize=True, figsize=(10, 6)):
    """Plot overall sequence length distribution with geometric overlay."""
    # Extract all sequences
    all_sequences = []
    for polymer in polymers:
        seqs = find_sequences(polymer, monomer_id)
        all_sequences.extend([length for _, length in seqs])

    # Calculate statistics
    mean_length = np.mean(all_sequences)
    max_length = max(all_sequences)

    # Create bins for histogram
    bins = np.arange(0.5, max_length + 1.5, 1)

    # Plot histogram
    plt.figure(figsize=figsize)
    counts, _, _ = plt.hist(
        all_sequences,
        bins=bins,
        alpha=0.7,
        edgecolor="black",
        density=normalize,
        label="Observed",
    )

    # Plot geometric distribution
    x_values = np.arange(1, max_length + 1)
    if normalize:
        p = 1 / mean_length
        y_geo = [(1 - p) ** (k - 1) * p for k in x_values]
    else:
        p = 1 / mean_length
        y_geo = [((1 - p) ** (k - 1) * p) * len(all_sequences) for k in x_values]

    plt.plot(x_values, y_geo, "r-o", markersize=4, alpha=0.8, label="Geometric")

    plt.xlabel("Sequence Length")
    plt.ylabel("Probability" if normalize else "Count")
    plt.title(
        f"{'A' if monomer_id==3 else 'B'} Monomer Sequence Distribution\nMean: {mean_length:.2f}"
    )
    plt.legend()

    plt.xlim(0.5, max_length + 0.5)
    plt.xticks(np.arange(1, max_length + 1, 1))

    return plt.gcf()


def plot_positional_analysis(
    polymer_file, monomer_ids=[3, 4], num_buckets=10, n_bootstrap=1000, confidence=0.95
):
    """
    Plot sequence length distributions by position with bootstrap confidence intervals.

    Uses fractional assignment approach for more accurate position representation.
    """
    polymers = read_polymer_file(polymer_file)

    plt.figure(figsize=(12, 7))
    colors = ["b", "r"]
    labels = ["A Monomer", "B Monomer"]

    x = np.linspace(0, 1, num_buckets)

    for idx, monomer_id in enumerate(monomer_ids):
        # Get sequence data by position bucket with fractional assignment
        bucket_data = analyze_sequences_fractional(polymers, monomer_id, num_buckets)

        # Calculate statistics with bootstrap confidence intervals
        means = []
        lower_bounds = []
        upper_bounds = []
        geo_lower = []
        geo_upper = []

        for bucket in bucket_data:
            mean, lower, upper = bootstrap_statistics(bucket, n_bootstrap, confidence)
            means.append(mean)

            if lower is not None and upper is not None:
                lower_bounds.append(lower)
                upper_bounds.append(upper)

                # Calculate geometric distribution confidence intervals
                g_lower, g_upper = geometric_bootstrap(
                    mean, len(bucket), n_bootstrap, confidence
                )
                geo_lower.append(g_lower if g_lower is not None else mean)
                geo_upper.append(g_upper if g_upper is not None else mean)
            else:
                # Handle buckets with insufficient data
                lower_bounds.append(mean if mean > 0 else 1)
                upper_bounds.append(mean if mean > 0 else 1)
                geo_lower.append(mean if mean > 0 else 1)
                geo_upper.append(mean if mean > 0 else 1)

        # Convert to arrays
        means = np.array(means)
        lower_bounds = np.array(lower_bounds)
        upper_bounds = np.array(upper_bounds)
        geo_lower = np.array(geo_lower)
        geo_upper = np.array(geo_upper)

        # Plot mean as line
        plt.plot(x, means, f"{colors[idx]}-", linewidth=2, label=f"{labels[idx]} Mean")

        # Plot bootstrap confidence intervals as semi-transparent filled region
        plt.fill_between(
            x,
            lower_bounds,
            upper_bounds,
            color=colors[idx],
            alpha=0.2,
            label=f"{labels[idx]} 95% CI",
        )

        # Plot theoretical geometric distribution bounds as dashed lines
        plt.plot(
            x,
            geo_upper,
            f"{colors[idx]}--",
            alpha=0.7,
            label=f"{labels[idx]} Geometric CI",
        )
        plt.plot(x, geo_lower, f"{colors[idx]}--", alpha=0.7)

    plt.xlabel("Relative Position in Polymer", fontsize=12)
    plt.ylabel("Sequence Length", fontsize=12)
    plt.title(
        f"Sequence Length vs Position ({num_buckets} buckets)\nWith Bootstrap 95% Confidence Intervals",
        fontsize=14,
    )
    plt.legend()
    plt.grid(alpha=0.3)

    return plt.gcf()


def plot_positional_sequence_distribution(
    polymer_file, monomer_ids=[3, 4], num_buckets=10, confidence=0.9
):
    """
    Plot sequence length by position showing actual data spread via percentiles.

    Parameters:
    -----------
    polymer_file : str
        Path to polymer data file
    monomer_ids : list
        List of monomer types to analyze
    num_buckets : int
        Number of position buckets
    confidence : float
        Confidence level (e.g., 0.9 shows 5th and 95th percentiles)
    """
    polymers = read_polymer_file(polymer_file)

    plt.figure(figsize=(12, 7))
    colors = ["b", "r"]
    labels = ["A Monomer", "B Monomer"]

    x = np.linspace(0, 1, num_buckets)
    lower_pct = (1 - confidence) / 2 * 100
    upper_pct = (1 - (1 - confidence) / 2) * 100

    for idx, monomer_id in enumerate(monomer_ids):
        bucket_data = analyze_sequences_fractional(polymers, monomer_id, num_buckets)

        means = []
        lower_bounds = []
        upper_bounds = []

        for bucket in bucket_data:
            if len(bucket) > 1:
                mean = np.mean(bucket)
                means.append(mean)
                lower_bounds.append(max(1, np.percentile(bucket, lower_pct)))
                upper_bounds.append(np.percentile(bucket, upper_pct))
            else:
                # Handle insufficient data
                mean = np.mean(bucket) if len(bucket) > 0 else 1
                means.append(mean)
                lower_bounds.append(mean)
                upper_bounds.append(mean)

        # Convert to arrays
        means = np.array(means)
        lower_bounds = np.array(lower_bounds)
        upper_bounds = np.array(upper_bounds)

        # Plot mean as line
        plt.plot(x, means, f"{colors[idx]}-", linewidth=2, label=f"{labels[idx]} Mean")

        # Plot percentile bounds as semi-transparent band
        plt.fill_between(
            x,
            lower_bounds,
            upper_bounds,
            color=colors[idx],
            alpha=0.2,
            label=f"{labels[idx]} {int(confidence*100)}% Data Range",
        )

        # Calculate and plot theoretical geometric percentiles
        geo_lower = []
        geo_upper = []

        for mean in means:
            if mean > 1:
                p = 1 / mean  # Geometric parameter
                # Generate theoretical distribution
                theo_samples = np.random.geometric(p, size=10000)
                geo_lower.append(max(1, np.percentile(theo_samples, lower_pct)))
                geo_upper.append(np.percentile(theo_samples, upper_pct))
            else:
                geo_lower.append(mean)
                geo_upper.append(mean)

        # Plot geometric percentiles as dashed lines
        plt.plot(
            x,
            geo_lower,
            f"{colors[idx]}--",
            alpha=0.7,
            label=f"{labels[idx]} Geo {int(confidence*100)}%",
        )
        plt.plot(x, geo_upper, f"{colors[idx]}--", alpha=0.7)

    plt.xlabel("Relative Position in Polymer", fontsize=12)
    plt.ylabel("Sequence Length", fontsize=12)
    plt.title(
        f"Sequence Length Distribution vs Position\nShowing {int(confidence*100)}% Data Range",
        fontsize=14,
    )
    plt.legend()
    plt.grid(alpha=0.3)

    return plt.gcf()


def plot_sequence_asymmetric_errors(
    polymer_file,
    monomer_ids=[3, 4],
    num_buckets=10,
    quantiles=[0.25, 0.75],
    secondary_quantiles=[0.05, 0.95],
):
    """
    Plot sequence length distribution with asymmetric error bars.

    Parameters:
    -----------
    polymer_file : str
        Path to polymer data file
    monomer_ids : list
        List of monomer types to analyze
    num_buckets : int
        Number of position buckets
    quantiles : list
        Primary quantiles for inner error bars (default: quartiles)
    secondary_quantiles : list
        Secondary quantiles for outer error bars (default: 5th/95th percentiles)
    """
    polymers = read_polymer_file(polymer_file)

    plt.figure(figsize=(12, 7))
    colors = ["b", "r"]
    labels = ["A Monomer", "B Monomer"]
    marker_styles = ["o", "s"]

    x = np.linspace(0, 1, num_buckets)
    x_offset = [-0.01, 0.01]  # Offset to avoid overlap

    for idx, monomer_id in enumerate(monomer_ids):
        bucket_data = analyze_sequences_fractional(polymers, monomer_id, num_buckets)

        # Calculate statistics for each bucket
        means = []
        medians = []
        lower_q1 = []
        upper_q1 = []
        lower_q2 = []
        upper_q2 = []

        for bucket in bucket_data:
            if len(bucket) > 1:
                means.append(np.mean(bucket))
                medians.append(np.median(bucket))
                lower_q1.append(np.quantile(bucket, quantiles[0]))
                upper_q1.append(np.quantile(bucket, quantiles[1]))
                lower_q2.append(np.quantile(bucket, secondary_quantiles[0]))
                upper_q2.append(np.quantile(bucket, secondary_quantiles[1]))
            else:
                val = np.mean(bucket) if len(bucket) > 0 else 1
                means.append(val)
                medians.append(val)
                lower_q1.append(val)
                upper_q1.append(val)
                lower_q2.append(val)
                upper_q2.append(val)

        # Create error bar arrays
        primary_err_minus = np.array(means) - np.array(lower_q1)
        primary_err_plus = np.array(upper_q1) - np.array(means)

        secondary_err_minus = np.array(means) - np.array(lower_q2)
        secondary_err_plus = np.array(upper_q2) - np.array(means)

        # Plot with asymmetric error bars
        plt.errorbar(
            x + x_offset[idx],
            means,
            yerr=[primary_err_minus, primary_err_plus],
            fmt=marker_styles[idx],
            color=colors[idx],
            markersize=7,
            label=f"{labels[idx]} Mean",
            capsize=4,
            elinewidth=2,
        )

        # Plot secondary error bars (wider spread)
        plt.errorbar(
            x + x_offset[idx],
            means,
            yerr=[secondary_err_minus, secondary_err_plus],
            fmt="none",
            color=colors[idx],
            alpha=0.4,
            capsize=3,
            label=f"{labels[idx]} {int(secondary_quantiles[1]*100)}th percentile",
        )

        # Plot median line
        plt.plot(
            x + x_offset[idx],
            medians,
            marker_styles[idx],
            color=colors[idx],
            alpha=0.5,
            markersize=4,
            label=f"{labels[idx]} Median",
        )

        # Calculate and overlay geometric distribution bounds
        geo_quantiles = []
        for mean_val in means:
            if mean_val > 1:
                p = 1 / mean_val
                geo_samples = np.random.geometric(p, size=10000)
                q_vals = [
                    np.quantile(geo_samples, quantiles[0]),
                    np.quantile(geo_samples, quantiles[1]),
                    np.quantile(geo_samples, secondary_quantiles[0]),
                    np.quantile(geo_samples, secondary_quantiles[1]),
                ]
                geo_quantiles.append(q_vals)
            else:
                geo_quantiles.append([mean_val, mean_val, mean_val, mean_val])

        # Plot geometric expectation
        for i, (mean_val, quants) in enumerate(zip(means, geo_quantiles)):
            if mean_val > 1:
                plt.plot(
                    [x[i] + x_offset[idx], x[i] + x_offset[idx]],
                    [quants[0], quants[1]],
                    "--",
                    color=colors[idx],
                    alpha=0.6,
                )
                plt.plot(
                    [x[i] + x_offset[idx], x[i] + x_offset[idx]],
                    [quants[2], quants[3]],
                    ":",
                    color=colors[idx],
                    alpha=0.4,
                )

    plt.xlabel("Relative Position in Polymer", fontsize=12)
    plt.ylabel("Sequence Length", fontsize=12)
    plt.title("Sequence Length Distribution with Asymmetric Error Bars", fontsize=14)
    plt.grid(axis="y", alpha=0.3)

    # Custom legend to avoid redundant entries
    handles, labels = plt.gca().get_legend_handles_labels()
    unique_labels = []
    unique_handles = []
    for handle, label in zip(handles, labels):
        if label not in unique_labels:
            unique_labels.append(label)
            unique_handles.append(handle)

    plt.legend(unique_handles, unique_labels, loc="upper right")

    return plt.gcf()


def plot_position_heatmap(polymer_file, monomer_id=3, num_buckets=10):
    """Create a heatmap of sequence length distribution by position."""
    polymers = read_polymer_file(polymer_file)
    bucket_data = analyze_sequences_fractional(polymers, monomer_id, num_buckets)

    # Find maximum sequence length
    max_length = 1
    for bucket in bucket_data:
        if bucket:
            max_length = max(max_length, max(bucket))

    # Create 2D histogram matrix
    histogram = np.zeros((max_length, num_buckets))

    for bucket_idx, sequences in enumerate(bucket_data):
        for length in sequences:
            histogram[length - 1, bucket_idx] += 1

    # Normalize by column
    for col in range(num_buckets):
        col_sum = np.sum(histogram[:, col])
        if col_sum > 0:
            histogram[:, col] = histogram[:, col] / col_sum

    # Create heatmap
    plt.figure(figsize=(10, 6))
    plt.imshow(
        histogram,
        aspect="auto",
        origin="lower",
        extent=[0, 1, 1, max_length],
        cmap="viridis",
    )

    # Calculate and overlay mean sequence length at each position
    means = [np.mean(bucket) if bucket else 0 for bucket in bucket_data]
    x = np.linspace(0, 1, num_buckets)
    plt.plot(x, means, "r-", linewidth=2, label="Mean Length")

    plt.xlabel("Relative Position in Polymer")
    plt.ylabel("Sequence Length")
    plt.title(
        f'{"A" if monomer_id==3 else "B"} Monomer Sequence Distribution by Position'
    )
    plt.colorbar(label="Probability")
    plt.legend()

    return plt.gcf()
