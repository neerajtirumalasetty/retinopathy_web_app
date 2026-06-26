"""
main.py
-------
FastAPI backend entry point for the Diabetic Retinopathy Detection System.

Run with:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import traceback
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from model_loader import get_model, CLASS_NAMES
from predictor import run_inference
from explanation import generate_explanation, generate_recommendation, generate_safety_note

app = FastAPI(
    title="Diabetic Retinopathy Detection System API",
    description=(
        "Backend API for the SDP project 'Diabetic Retinopathy Detection System'. "
        "Loads a trained MobileNetV2 model and performs real-time inference on "
        "uploaded retinal fundus images."
    ),
    version="1.0.0",
)

# Allow the Vite dev server (and any frontend) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    risk: str
    recommendation: str
    medical_explanation: str
    safety_note: str
    class_probabilities: dict


@app.on_event("startup")
def load_model_on_startup():
    """
    Pre-load the model into memory when the server starts, so the first
    prediction request doesn't pay the model-loading latency cost.
    """
    try:
        get_model()
    except Exception as e:
        # We don't crash the server here -- /api/predict will raise a clear
        # error if the model truly isn't available, but this lets /health
        # still respond so the failure is easy to diagnose.
        print(f"[startup] WARNING: model failed to preload: {e}")


@app.get("/")
def root():
    return {
        "service": "Diabetic Retinopathy Detection System API",
        "status": "running",
        "model": "MobileNetV2 (best_mobilenetv2_gaussian.h5)",
        "classes": CLASS_NAMES,
    }


@app.get("/health")
def health_check():
    try:
        get_model()
        model_status = "loaded"
    except Exception as e:
        model_status = f"error: {e}"
    return {"status": "ok", "model_status": model_status}


@app.post("/api/predict", response_model=PredictionResponse)
async def predict(
    file: UploadFile = File(...),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    diabetic_history: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
    language: Optional[str] = Form("en"),
):
    """
    Accepts a retinal fundus image plus optional patient details and returns
    the CNN's diabetic retinopathy severity prediction along with a
    rule-based medical explanation, risk level, and recommended action.

    `language` controls the language of the generated explanation,
    recommendation, and safety note. Supported: "en", "hi", "te".
    Defaults to English if omitted or unrecognized.
    """
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    try:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        result = run_inference(file_bytes)

        explanation = generate_explanation(
            prediction=result["prediction"],
            confidence=result["confidence"],
            age=age,
            gender=gender,
            diabetic_history=diabetic_history,
            symptoms=symptoms,
            language=language,
        )
        recommendation = generate_recommendation(result["prediction"], language=language)
        safety_note = generate_safety_note(result["prediction"], language=language)

        return PredictionResponse(
            prediction=result["prediction"],
            confidence=result["confidence"],
            risk=result["risk"],
            recommendation=recommendation,
            medical_explanation=explanation,
            safety_note=safety_note,
            class_probabilities=result["class_probabilities"],
        )

    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
