"""
Author: 'Jacob Haas via github.com/ahoarfrost/fastBio'

Loads the data and trains Plastiscope from scratch using LookingGlass architecture.
"""

from fastBio import LookingGlass
from fastai.text import load_data
import torch
import os
import time
import random
from utils import log_step

# === Settings ===
EPOCHS = 1
BATCH_SIZE = 512
SEED = 42

random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
os.environ["PYTHONHASHSEED"] = str(SEED)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

start = time.time()
log_step("Start loading LMDataBunch")

lmdata = load_data("models", "plastiscope_LMbunch.pkl")
log_step("Loaded LMDataBunch")

# === Train Model ===
print("Creating Plastiscope model...")
learner = LookingGlass(data=lmdata).load(pretrained=False)

log_step("Start model training")
learner.fit_one_cycle(EPOCHS)
log_step("Finished model training")

# === Save ===
learner.save("plastiscope")
learner.export("plastiscope_export.pkl")
torch.save(learner.model[0].state_dict(), lmdata.path / "plastiscope_25g_enc.pth")

log_step("Saved model and encoder")
print(f"Total runtime: {(time.time() - start):.2f}s")

