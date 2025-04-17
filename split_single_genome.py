"""
Author: Jacob Haas

Splits a full genome FASTA file into short DNA reads between 60 and 300 bp.

Settings:
- INPUT_FILE: Path to genome FASTA file
- OUTPUT_FOLDER: Directory to store short reads
- MIN_LEN, MAX_LEN, MEAN_LEN: Control Gaussian-distributed read lengths

The script generates a new FASTA file with synthetic short reads,
saving progress using tqdm and writing the output to the specified folder.
"""

import os
import random
from pathlib import Path
from Bio import SeqIO
from tqdm import tqdm

# Constants
INPUT_FILE = Path("../LMJ/genome.fasta")
OUTPUT_FOLDER = Path("lmj_short_reads")
MIN_LEN = 60
MAX_LEN = 300
MEAN_LEN = 136

def split_fasta(input_file, output_folder):
    genome_name = input_file.stem
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / f"{genome_name}_reads.fasta"

    total_bases = sum(len(record.seq) for record in SeqIO.parse(str(input_file), "fasta"))

    with open(output_file, "w") as f, tqdm(total=total_bases, desc=f"Processing {genome_name}", unit="bp") as pbar:
        for record in SeqIO.parse(str(input_file), "fasta"):
            seq = str(record.seq)
            i = 0
            while i < len(seq):
                read_len = max(MIN_LEN, min(MAX_LEN, int(random.gauss(MEAN_LEN, 30))))
                chunk = seq[i:i+read_len]
                if len(chunk) >= MIN_LEN:
                    f.write(f">read_{i}\n{chunk}\n")
                i += read_len
                pbar.update(read_len)

if __name__ == "__main__":
    split_fasta(INPUT_FILE, OUTPUT_FOLDER)
    print(f"Done. Short reads saved in: {OUTPUT_FOLDER}")

