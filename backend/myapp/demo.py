import os
import warnings
from glob import glob
from pathlib import Path
import cv2
import numpy as np
import PIL.Image
import torch
from PIL import Image
from tqdm import tqdm

from .lib.model_zoo.migan_inference import Generator as MIGAN

warnings.filterwarnings("ignore")


def read_mask(mask_path, invert=False):
    mask = Image.open(mask_path)
    print(f"mask mode: {mask.mode}")
    mask = resize(mask, max_size=512, interpolation=Image.NEAREST)
    mask = np.array(mask)
    if len(mask.shape) == 3:
        if mask.shape[2] == 4:
            _r, _g, _b, _a = np.rollaxis(mask, axis=-1)
            mask = np.dstack([_a, _a, _a])
        elif mask.shape[2] == 2:
            _l, _a = np.rollaxis(mask, axis=-1)
            mask = np.dstack([_a, _a, _a])
        elif mask.shape[2] == 3:
            _r, _g, _b = np.rollaxis(mask, axis=-1)
            mask = np.dstack([_r, _r, _r])
    else:
        mask = np.dstack([mask, mask, mask])
    if invert:
        mask = 255 - mask
    mask[mask < 255] = 0
    return Image.fromarray(mask).convert("L")


def resize(image, max_size, interpolation=Image.BICUBIC):
    w, h = image.size
    if w > max_size or h > max_size:
        resize_ratio = max_size / w if w > h else max_size / h
        image = image.resize((int(w * resize_ratio), int(h * resize_ratio)), interpolation)
    return image


def preprocess(img: Image, mask: Image, resolution: int) -> torch.Tensor:
    img = img.resize((resolution, resolution), Image.BICUBIC)
    mask = mask.resize((resolution, resolution), Image.NEAREST)
    img = np.array(img)
    mask = np.array(mask)[:, :, np.newaxis] // 255
    img = torch.Tensor(img).float() * 2 / 255 - 1
    mask = torch.Tensor(mask).float()
    img = img.permute(2, 0, 1).unsqueeze(0)
    mask = mask.permute(2, 0, 1).unsqueeze(0)
    x = torch.cat([mask - 0.5, img * mask], dim=1)
    return x


def main(model_name, model_path, img_path, mask_path, output_path, invert):
    if model_name == "migan-256":
        resolution = 256
        model = MIGAN(resolution=256)
    elif model_name == "migan-512":
        resolution = 512
        model = MIGAN(resolution=512)
    else:
        raise Exception("Unsupported model name.")

    model.load_state_dict(torch.load(model_path))
    model.eval()

    img = Image.open(img_path).convert("RGB")
    print(f"img mode: {img.mode}")
    img_resized = resize(img, max_size=resolution)
    mask = read_mask(mask_path, invert=invert)
    mask_resized = resize(mask, max_size=resolution, interpolation=Image.NEAREST)

    x = preprocess(img_resized, mask_resized, resolution)
    with torch.no_grad():
        result_image = model(x)[0]

    result_image = (result_image * 0.5 + 0.5).clamp(0, 1) * 255
    result_image = result_image.to(torch.uint8).permute(1, 2, 0).detach().to("cpu").numpy()

    result_image = cv2.resize(result_image, dsize=img_resized.size, interpolation=cv2.INTER_CUBIC)
    mask_resized = np.array(mask_resized)[:, :, np.newaxis] // 255
    composed_img = img_resized * mask_resized + result_image * (1 - mask_resized)
    composed_img = Image.fromarray(composed_img)
    composed_img.save(f"{output_path}/{Path(img_path).stem}.png")

