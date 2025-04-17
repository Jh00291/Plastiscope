"""
Author: Jacob Haas

"""

import os
import random
import time
from pathlib import Path
from Bio import SeqIO
from tqdm import tqdm


# Constants
GENOMES_DIR = "genomes"
OUTPUT_DIR = "genomes_short_reads"
MIN_LEN = 60
MAX_LEN = 300
MEAN_LEN = 136

def split_fasta(input_file, output_folder, min_len=MIN_LEN, max_len=MAX_LEN, mean_len=MEAN_LEN):
    """
    Splits a genome FASTA file into random short reads and saves them to a new FASTA file.

    Parameters:
        input_file (str or Path): Path to the input FASTA file.
        output_folder (str or Path): Directory where output FASTA will be stored.
        min_len (int): Minimum read length.
        max_len (int): Maximum read length.
        mean_len (int): Mean read length (used in Gaussian distribution).
    """

    genome_name = Path(input_file).stem
    genome_output_dir = Path(output_folder) / genome_name
    genome_output_dir.mkdir(parents=True, exist_ok=True)

    output_file = genome_output_dir / f"{genome_name}_reads.fasta"

    # Count total bases for progress tracking
    total_bases = sum(len(record.seq) for record in SeqIO.parse(input_file, "fasta"))

    with open(output_file, "w") as f, tqdm(total=total_bases, desc=f"Processing {genome_name}", unit="bp", leave=True) as pbar:
        for record in SeqIO.parse(input_file, "fasta"):
            seq = str(record.seq)
            i = 0
            while i < len(seq):
                read_length = max(min_len, min(max_len, int(random.gauss(mean_len, 30))))
                chunk = seq[i:i+read_length]
                if len(chunk) >= min_len:
                    f.write(f">read_{i}\n{chunk}\n")
                i += read_length
                pbar.update(read_length)

def process_all_genomes(input_dir=GENOMES_DIR, output_dir=OUTPUT_DIR):
    """
    Processes all FASTA/FNA files in the input directory, splitting each into short reads.

    Parameters:
        input_dir (str or Path): Path to the input directory containing FASTA/FNA files.
        output_dir (str or Path): Path to the directory where output will be saved.
    """

    start_time = time.time()

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fasta_files = list(Path(input_dir).glob("*.fna")) + list(Path(input_dir).glob("*.fasta"))

    if not fasta_files:
        print("No FASTA/FNA files found. Exiting.")
        return

    print(f"Found {len(fasta_files)} genome files. Splitting into short reads...\n")

    for file in fasta_files:
        split_fasta(file, output_dir)

    total_elapsed_time = time.time() - start_time
    print(f"\nProcessing completed in {total_elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    process_all_genomes()
