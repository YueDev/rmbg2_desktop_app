#!/usr/bin/env python3
"""RMBG 2.0 Background Removal Module"""

import os

import numpy as np
import onnxruntime as ort
from PIL import Image

ort.set_default_logger_severity(3)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "rmbg20_model_fp16.onnx")
INPUT_SIZE = 1024
MEAN = [0.5, 0.5, 0.5]
STD = [1.0, 1.0, 1.0]

_session = None


def _get_session():
    """Get or create global session"""
    global _session
    if _session is None:
        print(f"Loading model from: {MODEL_PATH}")
        # CoreML for Apple Silicon GPU, CUDA for NVIDIA GPU, CPU fallback
        available = ort.get_available_providers()
        if "CoreMLExecutionProvider" in available:
            providers = ["CoreMLExecutionProvider", "CPUExecutionProvider"]
        elif "CUDAExecutionProvider" in available:
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        else:
            providers = ["CPUExecutionProvider"]

        sess_options = ort.SessionOptions()
        # 兼容 macOS 的 FP16 CoreML，防止 LayerNormFusion 因为类型转换失败崩溃
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC

        _session = ort.InferenceSession(MODEL_PATH, sess_options=sess_options, providers=providers)
        print(f"Model loaded. Provider: {providers[0]}")
        print(f"Inputs: {[i.name for i in _session.get_inputs()]}")
    return _session


def preprocess_image(image: Image.Image):
    if image.mode != "RGB":
        image = image.convert("RGB")
    orig_w, orig_h = image.size
    image = image.resize((INPUT_SIZE, INPUT_SIZE), Image.Resampling.LANCZOS)
    img_array = np.array(image, dtype=np.float32) / 255.0
    for i in range(3):
        img_array[:, :, i] = (img_array[:, :, i] - MEAN[i]) / STD[i]
    img_array = np.transpose(img_array, (2, 0, 1))
    img_array = np.expand_dims(img_array, axis=0)
    return img_array, orig_w, orig_h


def postprocess_mask(mask, orig_w, orig_h):
    mask = mask.squeeze()
    mask_min, mask_max = mask.min(), mask.max()
    if mask_max - mask_min > 1e-6:
        mask = (mask - mask_min) / (mask_max - mask_min)
    mask = (mask * 255).astype(np.uint8)
    mask_image = Image.fromarray(mask, mode="L")
    return mask_image.resize((orig_w, orig_h), Image.Resampling.LANCZOS)


def remove_background(image: Image.Image) -> Image.Image:
    """
    Remove background from PIL Image.

    Args:
        image: PIL Image object

    Returns:
        PIL Image with transparent background (RGBA mode)
    """
    session = _get_session()
    print(f"Using provider: {session.get_providers()[0]}")
    orig_w, orig_h = image.size
    input_data, _, _ = preprocess_image(image)
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    result = session.run([output_name], {input_name: input_data})
    mask_image = postprocess_mask(result[0], orig_w, orig_h)
    result_image = image.convert("RGBA")
    result_image.putalpha(mask_image)
    return result_image


def remove_background_from_file(file_path: str) -> Image.Image:
    """
    Remove background from image file.

    Args:
        file_path: Path to image file

    Returns:
        PIL Image with transparent background (RGBA mode)
    """
    image = Image.open(file_path)
    return remove_background(image)


def is_model_loaded() -> bool:
    """Check if model is loaded"""
    return _session is not None
