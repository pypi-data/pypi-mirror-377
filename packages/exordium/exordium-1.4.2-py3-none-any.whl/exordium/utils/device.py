import torch


def get_device_str(gpu_id: int | None = None) -> str:
    if torch.backends.mps.is_available():
        # Apple Silicon GPU
        return "mps" if gpu_id is None else f"mps:{gpu_id}"
    elif torch.cuda.is_available():
        # Nvidia GPU
        if gpu_id is not None and gpu_id < torch.cuda.device_count():
            return "cuda" if gpu_id is None else f"cuda:{gpu_id}"
        else:
            print(f"Warning: cuda device {gpu_id} not available, falling back to cpu.")
            return "cpu"
    else:
        # fallback to CPU
        return "cpu"


def get_torch_device(gpu_id: int | None = None) -> torch.device:
    return torch.device(get_device_str(gpu_id))

