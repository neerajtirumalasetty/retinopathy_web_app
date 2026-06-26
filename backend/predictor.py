"""
predictor.py
------------
Handles image preprocessing and inference using the loaded MobileNetV2 model.
"""

import io
import numpy as np
from PIL import Image

from model_loader import get_model, CLASS_NAMES, IMAGE_SIZE

RISK_MAP = {
    "No_DR": "Low",
    "Mild": "Low",
    "Moderate": "Medium",
    "Severe": "High",
    "Proliferative_DR": "Critical",
}


def preprocess_image(file_bytes: bytes) -> np.ndarray:
    """
    Converts raw uploaded image bytes into a model-ready tensor.

    Steps:
      1. Load image from bytes
      2. Convert to RGB (drops alpha / handles grayscale)
      3. Resize to 224x224
      4. Normalize to [0, 1]
      5. Expand dims to create a batch of size 1
    """
    image = Image.open(io.BytesIO(file_bytes))
    image = image.convert("RGB")
    image = image.resize(IMAGE_SIZE)

    img_array = np.array(image).astype("float32")
    img_array = img_array / 255.0  # matches training pipeline normalization
    img_array = np.expand_dims(img_array, axis=0)  # (1, 224, 224, 3)

    return img_array


def run_inference(file_bytes: bytes) -> dict:
    """
    Runs the full inference pipeline on an uploaded retinal image and
    returns the predicted class, confidence score, and risk level.
    """
    model = get_model()
    img_tensor = preprocess_image(file_bytes)

    predictions = model.predict(img_tensor, verbose=0)
    probabilities = predictions[0]

    class_index = int(np.argmax(probabilities))
    predicted_class = CLASS_NAMES[class_index]
    confidence = float(np.max(probabilities)) * 100.0
    risk = RISK_MAP.get(predicted_class, "Unknown")

    # Per-class probability breakdown (useful for the frontend / debugging)
    class_probabilities = {
        CLASS_NAMES[i]: round(float(probabilities[i]) * 100.0, 2)
        for i in range(len(CLASS_NAMES))
    }

    return {
        "prediction": predicted_class,
        "confidence": round(confidence, 2),
        "risk": risk,
        "class_probabilities": class_probabilities,
    }
