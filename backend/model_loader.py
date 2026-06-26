"""
model_loader.py
----------------
Loads the trained MobileNetV2 (.h5) model exactly once and exposes it as a
singleton so FastAPI doesn't reload the model on every request.
"""

import os
import threading
import tensorflow as tf

# Path to the production model (MobileNetV2 - best validation accuracy ~73.8%)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "best_mobilenetv2_gaussian.h5")

CLASS_NAMES = [
    "Mild",
    "Moderate",
    "No_DR",
    "Proliferative_DR",
    "Severe",
]

IMAGE_SIZE = (224, 224)

_model = None
_lock = threading.Lock()


def get_model():
    """
    Returns a cached singleton instance of the Keras model.
    Thread-safe lazy loading so the model is only loaded into memory once,
    the first time a prediction is requested (or at startup, see main.py).
    """
    global _model
    if _model is None:
        with _lock:
            if _model is None:  # double-checked locking
                if not os.path.exists(MODEL_PATH):
                    raise FileNotFoundError(
                        f"Model file not found at {MODEL_PATH}. "
                        f"Place best_mobilenetv2_gaussian.h5 inside backend/models/"
                    )
                print(f"[model_loader] Loading model from {MODEL_PATH} ...")
                _model = tf.keras.models.load_model(MODEL_PATH, compile=False)
                print("[model_loader] Model loaded successfully.")
    return _model
