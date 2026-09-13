import json
import numpy as np

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# SETTINGS
# ============================================================

MODEL_PATH = "model/gru_overlay_detection_best.keras"
VOCAB_PATH = "model/event_to_id.json"

MAX_LENGTH = 3000


# ============================================================
# LOAD MODEL + VOCABULARY ONCE
# ============================================================

print("Loading model...")

model = load_model(MODEL_PATH)

print("Model loaded.")

with open(VOCAB_PATH, "r", encoding="utf-8") as file:
    event_to_id = json.load(file)

print("Vocabulary loaded.")
print("Vocabulary size:", len(event_to_id))


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="GRU Overlay Detection API"
)

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class EventRequest(BaseModel):
    session_id: str
    question_id: str
    timestamp: int
    answer_length: int
    blur_count: int
    event: dict


# ============================================================
# FRONTEND EVENT → TRAINING EVENT
# ============================================================
def convert_event(item: EventRequest):

    event_type = item.event.get("type")
    key = item.event.get("key")

    # ========================================================
    # KEY DOWN
    # ========================================================

    if event_type == "keydown":

        if key is None:
            return None

        key_mapping = {
            " ": "SPACE",
            "Shift": "SHIFT",
            "Control": "CTRL",
            "Alt": "ALT",
            "Meta": "COMMAND",
            "Enter": "ENTER",
            "Tab": "TAB",
            "Escape": "ESC",
            "Backspace": "BKSP",
            "Delete": "DELETE",
            "End": "END",
            "Home": "HOME",
            "Insert": "INSERT",
            "ContextMenu": "MENU",

            "NumLock": "NUM_LK",
            "PageDown": "PG_DOWN",

            "ArrowLeft": "ARW_LEFT",
            "ArrowRight": "ARW_RIGHT",
            "ArrowUp": "ARW_UP",
            "ArrowDown": "ARw_DOWN",

            "Meta": "COMMAND",
        }

        normalized_key = key_mapping.get(key, key)

        return f"KEY_DOWN({normalized_key})"


    # ========================================================
    # KEY UP
    # ========================================================

    if event_type == "keyup":

        if key is None:
            return None

        key_mapping = {
            " ": "SPACE",
            "Shift": "SHIFT",
            "Control": "CTRL",
            "Alt": "ALT",
            "Meta": "COMMAND",
            "Enter": "ENTER",
            "Tab": "TAB",
            "Escape": "ESC",
            "Backspace": "BKSP",
            "Delete": "DELETE",
            "End": "END",
            "Home": "HOME",
            "Insert": "INSERT",
            "ContextMenu": "MENU",

            "NumLock": "NUM_LK",
            "PageDown": "PG_DOWN",

            "ArrowLeft": "ARW_LEFT",
            "ArrowRight": "ARW_RIGHT",
            "ArrowUp": "ARW_UP",
            "ArrowDown": "ARw_DOWN",
        }

        normalized_key = key_mapping.get(key, key)

        return f"KEY_UP({normalized_key})"


    # ========================================================
    # FOCUS
    # ========================================================

    if event_type == "focus_change":

        return "FOCUS_CHANGED"


    # ========================================================
    # VISIBILITY
    # ========================================================

    if event_type == "visibility_change":

        return "VISIBILITY_CHANGED"


    # ========================================================
    # ANSWER LENGTH
    # ========================================================

    if event_type == "answer_length_change":

        return "ANSWER_LENGTH_CHANGED"


    return None

# ============================================================
# EVENTS → INTEGER IDs
# ============================================================

def events_to_ids(events):

    ids = []

    for event in events:

        if event is None:
            continue

        event_id = event_to_id.get(
            event,
            event_to_id["<UNK>"]
        )

        ids.append(event_id)

    return ids


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def health_check():

    return {
        "status": "ok",
        "model_loaded": True,
        "vocabulary_size": len(event_to_id)
    }


# ============================================================
# PREDICTION API
# ============================================================

@app.post("/predict")
def predict(events: list[EventRequest]):

    if not events:

        raise HTTPException(
            status_code=400,
            detail="Events array cannot be empty."
        )


    # --------------------------------------------------------
    # Convert frontend events
    # --------------------------------------------------------

    converted_events = []

    for item in events:

        converted = convert_event(item)

        if converted is not None:

            converted_events.append(converted)


    if not converted_events:

        raise HTTPException(
            status_code=400,
            detail="No supported events found."
        )


    # --------------------------------------------------------
    # Convert events → IDs
    # --------------------------------------------------------

    event_ids = events_to_ids(
        converted_events
    )


    # --------------------------------------------------------
    # Pad to model input shape
    # --------------------------------------------------------

    X = pad_sequences(
        [event_ids],
        maxlen=MAX_LENGTH,
        padding="post",
        truncating="post",
        value=event_to_id["<PAD>"]
    )


    # --------------------------------------------------------
    # Predict
    # --------------------------------------------------------

    probability = float(
        model.predict(
            X,
            verbose=0
        )[0][0]
    )


    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    prediction = (
        "CHEATING"
        if probability >= 0.5
        else "NORMAL"
    )


    return {
        "probability": round(probability, 6),
        "prediction": prediction,
        "event_count": len(converted_events)
    }