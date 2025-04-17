"""
Author: 'Jacob Haas via github.com/ahoarfrost/fastBio'

Evaluates a trained encoder's performance on a held-out genome by computing validation loss.

This script loads:
- A specified encoder `.pth` file
- A vocabulary `.npy` file
- A FASTA file of short reads (LMJ data)

It builds a DataBunch from the sequences and computes validation loss.
Used to benchmark models like Plastiscope or LookingGlass.

Usage:
    python evaluate_model.py models/plastiscope_150g_enc.pth
"""

import argparse
import numpy as np
import pandas as pd
import torch
from pathlib import Path
from Bio import SeqIO
from fastai.text import TextLMDataBunch, Vocab
from fastBio import LookingGlass
from utils import log_step

def load_lmj_data(vocab_path, fasta_path, batch_size=512):
    """
    Loads short reads from a FASTA file and prepares a TextLMDataBunch for evaluation.

    Args:
        vocab_path (str): Path to the .npy vocabulary file.
        fasta_path (str): Path to the FASTA file with short reads.
        batch_size (int): Batch size for the DataBunch.

    Returns:
        TextLMDataBunch: Prepared data for model evaluation.
    """
    print("Loading LMJ short reads...")
    lmj_seqs = [str(record.seq) for record in SeqIO.parse(str(fasta_path), "fasta")]
    lmj_df = pd.DataFrame({'seq': lmj_seqs})

    vocab_array = np.load(vocab_path, allow_pickle=True).astype(object)
    model_vocab = Vocab(list(vocab_array))

    lmj_data = TextLMDataBunch.from_df(
        path=Path("."),
        train_df=lmj_df,
        valid_df=lmj_df,
        text_cols='seq',
        vocab=model_vocab,
        bs=batch_size
    )
    log_step("Loaded LMJ data")
    return lmj_data

def load_encoder_into_model(pth_path, databunch):
    """
    Loads a saved encoder state dict into a new LookingGlass model.

    Args:
        pth_path (str): Path to the saved encoder `.pth` file.
        databunch (TextLMDataBunch): DataBunch to attach to the model.

    Returns:
        Learner: LookingGlass model with the loaded encoder.
    """
    learner = LookingGlass(data=databunch).load(pretrained=False)
    learner.model[0].load_state_dict(torch.load(pth_path, map_location=torch.device('cuda' if torch.cuda.is_available() else 'cpu')))
    log_step("Loaded model encoder")
    return learner

def evaluate_model_loss(learner, label="Model"):
    """
    Computes the validation loss for the given model.

    Args:
        learner (Learner): The model to evaluate.
        label (str): Label used for display.

    Returns:
        float: The validation loss value.
    """
    learner.model.eval()
    loss = learner.validate()[0]
    print(f"{label} → Loss: {loss:.4f}")
    log_step("Finished evaluation")
    return loss

def main():
    """
    Command-line entry point.
    Loads model and data, then evaluates the model on LMJ short reads.
    """
    parser = argparse.ArgumentParser(description="Evaluate a single encoder on LMJ genome short reads.")
    parser.add_argument("encoder_path", type=str, help="Path to the encoder .pth file")
    parser.add_argument("--vocab_path", type=str, default="models/ngs_vocab_k1_withspecial.npy", help="Path to the vocab .npy file")
    parser.add_argument("--fasta_path", type=str, default="lmj_short_reads/genome_reads.fasta", help="Path to the LMJ FASTA file")

    args = parser.parse_args()

    data = load_lmj_data(args.vocab_path, args.fasta_path)
    learner = load_encoder_into_model(args.encoder_path, data)

    print("\nEvaluating model...\n")
    evaluate_model_loss(learner, label=Path(args.encoder_path).stem)

if __name__ == "__main__":
    main()

