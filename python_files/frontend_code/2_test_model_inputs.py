import json
import numpy as np

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences


MODEL_PATH = "../keystroke_dataset/gru_overlay_detection_best.keras"
VOCAB_PATH = "../keystroke_dataset/event_to_id.json"

MAX_LENGTH = 3000


# ============================================================
# LOAD VOCABULARY
# ============================================================

with open(VOCAB_PATH, "r", encoding="utf-8") as file:
    event_to_id = json.load(file)


# ============================================================
# LOAD MODEL
# ============================================================

model = load_model(MODEL_PATH)


# ============================================================
# TEST EVENTS
# ============================================================

events = [
    "KEY_DOWN(h)",
    "KEY_DOWN(i)",
    "KEY_UP(h)",
    "KEY_UP(i)",
    "KEY_DOWN(SPACE)",
    "KEY_UP(SPACE)",
    "KEY_DOWN(t)",
    "KEY_UP(t)",
    "KEY_DOWN(i)",
    "KEY_DOWN(s)",
    "KEY_UP(i)",
    "KEY_UP(s)"
]


# ============================================================
# EVENTS → IDs
# ============================================================

event_ids = [
    event_to_id.get(
        event,
        event_to_id["<UNK>"]
    )
    for event in events
]


print("\nEvents:")
print(events)

print("\nEvent IDs:")
print(event_ids)


# ============================================================
# PAD
# ============================================================

X = pad_sequences(
    [event_ids],
    maxlen=MAX_LENGTH,
    padding="post",
    truncating="post",
    value=event_to_id["<PAD>"]
)


print("\nInput shape:")
print(X.shape)


# ============================================================
# PREDICTION
# ============================================================

probability = float(
    model.predict(
        X,
        verbose=0
    )[0][0]
)


prediction = (
    1
    if probability >= 0.5
    else 0
)


print("\n================================")
print("PYTHON MODEL RESULT")
print("================================")

print("Probability:", probability)
print("Prediction :", prediction)

print(
    "Class:",
    "CHEATING" if prediction == 1 else "NORMAL"
)