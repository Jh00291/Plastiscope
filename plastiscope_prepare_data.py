"""
Author: 'Jacob Haas via github.com/ahoarfrost/fastBio'

Prepares and saves a TextLMDataBunch using new genomes from the short-reads directory.
"""

from fastBio import BioTokenizer, BioVocab
from fastai.text import TextLMDataBunch, Vocab
from pathlib import Path
from Bio import SeqIO
import pandas as pd
import numpy as np
import random
import os
import torch
from utils import log_step

# === Settings ===
SEED = 42
BATCH_SIZE = 512
MAX_GENOMES = 25

# === Reproducibility ===
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
os.environ["PYTHONHASHSEED"] = str(SEED)

# === Paths ===
BASE_DIR = Path("./genomes_sequence_reads/")
VOCAB_PATH = Path("models/ngs_vocab_k1_withspecial.npy")
USED_GENOMES_FILE = Path("models/used_genomes.txt")
TRAIN_CSV = Path("models/train_df.csv")
VALID_CSV = Path("models/valid_df.csv")
LM_BUNCH_OUT = Path("../models/plastiscope_LMbunch.pkl")

# === Load Vocab ===
vocab_array = np.load(VOCAB_PATH, allow_pickle=True).astype(object)
vocab = Vocab(list(vocab_array))

# === Load Used Genomes ===
used_genomes = set()
if USED_GENOMES_FILE.exists():
    with open(USED_GENOMES_FILE) as f:
        used_genomes = set(f.read().splitlines())

# === Scan for New FASTAs ===
log_step("Started scanning FASTA")
genome_dirs = sorted([d for d in BASE_DIR.iterdir() if d.is_dir()])
new_dirs = [d for d in genome_dirs if d.name not in used_genomes][:MAX_GENOMES - len(used_genomes)]

# === Use Saved CSVs or Add New Data ===
if not new_dirs:
    train_df = pd.read_csv(TRAIN_CSV)
    valid_df = pd.read_csv(VALID_CSV)
else:
    fasta_files = [f for g in new_dirs for f in g.rglob("*.fasta")]
    sequences = [str(record.seq) for file in fasta_files for record in SeqIO.parse(str(file), "fasta")]

    random.shuffle(sequences)
    split = int(0.8 * len(sequences))
    new_train = pd.DataFrame({'seq': sequences[:split]})
    new_valid = pd.DataFrame({'seq': sequences[split:]})

    if TRAIN_CSV.exists():
        train_df = pd.read_csv(TRAIN_CSV).append(new_train, ignore_index=True)
        valid_df = pd.read_csv(VALID_CSV).append(new_valid, ignore_index=True)
    else:
        train_df, valid_df = new_train, new_valid

    train_df.to_csv(TRAIN_CSV, index=False)
    valid_df.to_csv(VALID_CSV, index=False)
    with open(USED_GENOMES_FILE, 'a') as f:
        for g in new_dirs:
            f.write(f"{g.name}\n")

log_step("Split train/valid and created/loaded DataFrames")

# === Create LMDataBunch ===
log_step("Started LMDataBunch creation")
lmdata = TextLMDataBunch.from_df(
    path=BASE_DIR,
    train_df=train_df,
    valid_df=valid_df,
    text_cols='seq',
    vocab=vocab,
    bs=BATCH_SIZE
)

lmdata.save(LM_BUNCH_OUT)
log_step("Finished LMDataBunch creation")

print(f"Saved LMDataBunch to {LM_BUNCH_OUT}")

