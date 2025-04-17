import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from Bio import SeqIO
import matplotlib.ticker as ticker
from collections import Counter

# Define directories
GENOMES_READS_DIR = "genomes_short_reads"

def read_lengths_generator():
    """Yield read lengths one by one from all FASTA files."""
    for genome_folder in Path(GENOMES_READS_DIR).iterdir():
        if genome_folder.is_dir():
            fasta_files = list(genome_folder.glob("*_reads.fasta"))
            for fasta_file in fasta_files:
                print(f"Processing: {fasta_file}")
                for record in SeqIO.parse(fasta_file, "fasta"):
                    yield len(record.seq)

def plot_read_length_distribution():
    """Stream read lengths and plot histogram with minimal memory usage."""
    length_counter = Counter()
    total_reads = 0
    lengths = []

    for length in read_lengths_generator():
        length_counter[length] += 1
        lengths.append(length)
        total_reads += 1

    if total_reads == 0:
        print("No reads found. Make sure the genomes_short_reads directory is populated.")
        return

    lengths_array = np.array(lengths)
    mean_length = np.mean(lengths_array)
    median_length = np.median(lengths_array)
    min_length = np.min(lengths_array)
    max_length = np.max(lengths_array)
    std_dev = np.std(lengths_array)

    # Plot histogram
    plt.figure(figsize=(12, 8))
    plt.hist(lengths_array, bins=50, color="royalblue", edgecolor="black", alpha=0.85)

    plt.axvline(mean_length, color='red', linestyle='--', linewidth=2.5, label=f'Mean: {mean_length:.2f}')
    plt.axvline(median_length, color='green', linestyle='--', linewidth=2.5, label=f'Median: {median_length:.2f}')

    # Set titles and labels with larger font sizes
    plt.title("Sequence Length Distribution", fontsize=30)
    plt.xlabel("Read Length (bp)", fontsize=30)
    plt.ylabel("Frequency", fontsize=30)
    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    plt.legend(fontsize=30)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Format y-axis ticks with commas
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{int(x):,}'))

    print("\n--- Read Length Statistics ---")
    print(f"Total Reads: {total_reads}")
    print(f"Mean Length: {mean_length:.2f} bp")
    print(f"Median Length: {median_length:.2f} bp")
    print(f"Min Length: {min_length} bp")
    print(f"Max Length: {max_length} bp")
    print(f"Standard Deviation: {std_dev:.2f} bp\n")

    # Add total reads text cleanly in the top-right corner
    plt.text(0.98, 0.55, f'Total Reads: {total_reads:,}',
             fontsize=28, transform=plt.gca().transAxes,
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    output_plot = "short_read_distribution.png"
    plt.tight_layout()
    plt.savefig(output_plot, dpi=600)
    print(f"Plot saved as {output_plot}")

    plt.show()

if __name__ == "__main__":
    plot_read_length_distribution()

