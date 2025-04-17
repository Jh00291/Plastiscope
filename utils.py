"""
utils.py
Author: Jacob Haas

Utility functions for tracking runtime and memory usage during pipeline execution.

This module defines the `log_step()` function, which logs:
- Time elapsed since the last step
- Change in CPU memory usage (in MB)
- Change in GPU memory usage (in MB), if CUDA is available

"""

import time
import os
import psutil
import torch

_last_time = time.time()
_last_cpu_mem = psutil.Process(os.getpid()).memory_info().rss
_last_gpu_mem = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0

def log_step(message=""):
    """
    Logs time and memory usage since the last call to `log_step`.

    Parameters:
        message (str): Optional description of the current step.
    """
    global _last_time, _last_cpu_mem, _last_gpu_mem

    current_time = time.time()
    elapsed = current_time - _last_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    # CPU Memory delta
    current_cpu_mem = psutil.Process(os.getpid()).memory_info().rss
    cpu_mem_delta = (current_cpu_mem - _last_cpu_mem) / (1024 * 1024)

    # GPU Memory delta
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        current_gpu_mem = torch.cuda.memory_allocated()
        gpu_mem_delta = (current_gpu_mem - _last_gpu_mem) / (1024 * 1024)
    else:
        gpu_mem_delta = 0

    print(f"[{message}] Time: {minutes}m {seconds}s | CPU Mem Δ: {cpu_mem_delta:.2f} MB | GPU Mem Δ: {gpu_mem_delta:.2f} MB")

    _last_time = current_time
    _last_cpu_mem = current_cpu_mem
    _last_gpu_mem = current_gpu_mem if torch.cuda.is_available() else 0

