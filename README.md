
# Plastiscope Training Guide

## Environment Setup

### Step 1:

Installed Anaconda3/Conda on Ubuntu 22 Server Remotely with: 
wget https://repo.anaconda.com/archive/Anaconda3-2020.07-Linux-x86_64.sh

---

### Step 2:

Activate conda with: 
bash Anaconda3-2020.07-Linux-x86_64.sh 
Restart terminal (exit $SHELL) to have changes take effect and ssh back into server 
Initialize new conda environment with: 
conda create -n NAME python=3.6
Activate with:
conda activate NAME
I used conda activate conda-env

---

### Step 3:

Download pytorch 1.2 whl locally: https://download.pytorch.org/whl/cu100/torch/torch-1.2.0-cp36-cp36m-manylinux1_x86_64.whl

Use scp to transfer local whl file to Ubuntu server:
scp ~/Downloads/torch-1.2.0-cp36-cp36m-manylinux1_x86_64.whl jh00291@160.10.23.18:/home/jh00291/

Confirm whl file is in server

Use “pip install” with the name of the whl file:
pip install torch-1.2.0-cp36-cp36m-manylinux1_x86_64.whl

---

### Step 4:

Once installed, download fastBio
The dependencies required to properly install fastBio, include 
- Python >= 3.6 
- Fastai = 1.0.52 
- Biopython = 1.73 
- Torch = 1.2.0 
- Torchvision = 0.4.0

pip install fastBio

---

## Overview
This guide outlines the full workflow for downloading genomes from PlasticDB, splitting them into sequence reads, analyzing their
length distributions, preparing training data, and training the Plastiscope model. Each script is explained in order of execution.


### Step 1: Downloading Genomes from PlasticDB

**Script:** `get_all_plasticDB_genomes.sh`

**To run:**
nohup get_all_plasticDB_genomes.sh >> download_genomes_output.log 2>&1 &

**Purpose:**  
- Downloads degraders list from PlasticDB  
- Extracts organism names  
- Retrieves FASTA genomes from NCBI  

**Output:**  
`genomes/` directory containing `.fasta` files

---

### Step 2: Splitting Genomes into Reads

**Script:** `split_genomes.py`

**To run:**
nohup python split_genomes.py >> split_reads.log 2>&1 &

**Purpose:**  
- Converts genomes to random-length DNA reads (60–300bp)

**Output:**  
`genomes_short_reads/{GENOME_NAME}/*.fasta`

---

### Step 3 (Optional): Plot Read Length Distribution

**Script:** `plot_sequence_distribution.py`

**To run:**
python plot_sequence_distribution.py

**Output:**  
`short_read_distribution.png`

**Purpose:**  
- Plots histogram of read lengths across genomes

---

### Step 4: Prepare Training Data

**Script:** `plastiscope_prepare_data.py`

**To run:**
nohup python plastiscope_prepare_data.py >> plastiscope_prep_data.log 2>&1 &


**Purpose:**  
- Tokenizes reads  
- Builds `TextLMDataBunch`  

**Output:**  
- `plastiscope_LMbunch.pkl`  
- `train_df.csv`, `valid_df.csv`  
- `used_genomes.txt`

---

### Step 5: Train Plastiscope Model

**Script:** `plastiscope_train_model.py`

**To run:**
nohup python plastiscope_train_model.py >> plastiscope_train.log 2>&1 &

**Purpose:**  
- Trains AWD-LSTM on DNA reads  

**Output:**  
- `plastiscope_export.pkl` (full model)  
- `plastiscope_25g_enc.pth` (encoder)

---

### Step 6: Prepare a Single Genome for Evaluation

**Script:** `split_single_genome.py`

**To run:**
python split_single_genome.py

**Purpose:**  
- Splits a single genome (e.g. LMJ) into reads for evaluation  

**Output:**  
`lmj_short_reads/genome_reads.fasta`

---

### Step 7: Evaluate Model

**Script:** `evaluate_model.py`

**To run:**
python evaluate_model.py models/plastiscope_25g_enc.pth

**Purpose:**  
- Evaluates model on validation genome reads  

**Output:**  
- Printed loss and resource usage stats  

---

## Utility Script: `utils.py`

**Purpose:**  
- Logs time and memory usage between training steps  

**Key Function:** `log_step()`  
- Tracks CPU, GPU memory, and elapsed time

---
