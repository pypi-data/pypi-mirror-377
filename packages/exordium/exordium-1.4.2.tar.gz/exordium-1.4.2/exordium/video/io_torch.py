import os
from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset
import numpy as np
from torchvision.transforms.functional import to_pil_image
from exordium import PathType


class ImageSequenceReader(Dataset):

    def __init__(self, path: PathType, transform=None):
        self.path = Path(path)
        self.files = sorted(os.listdir(str(path)))
        self.transform = transform

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):

        with Image.open(self.path / self.files[idx]) as img:
            img.load()

        if self.transform is not None:
            return self.transform(img)

        return img


class ImageSequenceWriter:

    def __init__(self, path: PathType, extension: str = 'jpg'):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.extension = extension
        self.counter = 0

    def write(self, frames: np.ndarray):
        # frames == (T,C,H,W)
        for t in range(frames.shape[0]):
            to_pil_image(frames[t]).save(str(self.path / f'{str(self.counter).zfill(4)}.{self.extension}'))
            self.counter += 1
