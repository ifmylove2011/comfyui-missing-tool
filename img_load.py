import base64
import os
import logging
from io import BytesIO
import torch
import numpy as np
from PIL import Image
from PIL import ImageOps
import folder_paths


class LoadImageA:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {"required": {
            "rgba_mode": ("BOOLEAN", {"default": False}),
            "image": (sorted(files) + ["#DATA"], {"image_upload": True})
            }
        }

    CATEGORY = "missed-tool"

    RETURN_TYPES = ("IMAGE", "MASK", "STRING",)
    RETURN_NAMES = ("image", "mask", "image_path",)
    FUNCTION = "load_image"

    def load_image(self, image, rgba_mode):
        image_path = folder_paths.get_annotated_filepath(image)
        i = Image.open(image_path)
        if rgba_mode:
            image = i.convert("RGBA")
        else:
            image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        if 'A' in i.getbands():
            mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
        return image, mask.unsqueeze(0), image_path
