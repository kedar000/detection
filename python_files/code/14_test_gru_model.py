"""
GRU Final Model Testing
=======================

This script performs the final evaluation of the trained GRU model.

It does NOT train the model.

It:
    1. Loads the previously trained GRU model.
    2. Recreates the same fixed event vocabulary used during training.
    3. Loads test_use_for_final.csv.
    4. Splits each input sequence using '|'.
    5. Converts events into their corresponding integer IDs.
    6. Converts unknown events into <UNK>.
    7. Pads all sequences to MAX_LENGTH = 3000.
    8. Runs the trained GRU model on the final test data.
    9. Calculates:
           - Accuracy
           - Precision
           - Recall
           - F1 Score
           - Confusion Matrix
    10. Displays the prediction for each final test sample.

Important:
    test_use_for_final.csv is used ONLY for final testing.
    It is not used for training or validation.
"""


import pandas as pd

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)


# ============================================================
# 1. SETTINGS
# ============================================================

MODEL_PATH = (
    "../keystroke_dataset/"
    "gru_overlay_detection_best.keras"
)

FINAL_TEST_PATH = (
    "../keystroke_dataset/"
    "test_use_for_final.csv"
)

MAX_LENGTH = 3000


# ============================================================
# 2. CREATE THE SAME FIXED VOCABULARY
# ============================================================

event_to_id = {
    "<PAD>": 0,
    "<UNK>": 1
}


# ------------------------------------------------------------
# Printable ASCII characters
# ------------------------------------------------------------

for ascii_code in range(33, 127):

    char = chr(ascii_code)

    down_event = f"KEY_DOWN({char})"
    up_event = f"KEY_UP({char})"

    event_to_id[down_event] = len(event_to_id)
    event_to_id[up_event] = len(event_to_id)


# ------------------------------------------------------------
# Special keyboard events
# ------------------------------------------------------------

special_keys = [
    "SHIFT",
    "CTRL",
    "ALT",
    "COMMAND",
    "SPACE",
    "ENTER",
    "TAB",
    "ESC",

    "BKSP",
    "CAPS_LOCK",
    "DELETE",
    "END",
    "HOME",
    "INSERT",
    "MENU",

    "NUM_1",
    "NUM_2",
    "NUM_4",
    "NUM_LK",

    "PG_DOWN",

    "WIN",

    "ARW_LEFT",
    "ARW_RIGHT",
    "ARW_UP",
    "ARw_DOWN",
]


for key in special_keys:

    down_event = f"KEY_DOWN({key})"
    up_event = f"KEY_UP({key})"

    event_to_id[down_event] = len(event_to_id)
    event_to_id[up_event] = len(event_to_id)


# ------------------------------------------------------------
# Application / browser events
# ------------------------------------------------------------

other_events = [
    "FOCUS_CHANGED",
    "VISIBILITY_CHANGED",
    "ANSWER_LENGTH_CHANGED",
]


for event in other_events:

    event_to_id[event] = len(event_to_id)


# ============================================================
# 3. PRINT VOCABULARY INFORMATION
# ============================================================

print("\n================================================")
print("VOCABULARY")
print("================================================")

print("Vocabulary size:", len(event_to_id))

print("PAD ID :", event_to_id["<PAD>"])
print("UNK ID :", event_to_id["<UNK>"])


# ============================================================
# 4. LOAD FINAL TEST CSV
# ============================================================

final_test_df = pd.read_csv(FINAL_TEST_PATH)


print("\n================================================")
print("FINAL TEST DATA")
print("================================================")

print("Final test samples:", len(final_test_df))

print("Columns:", final_test_df.columns.tolist())


# ============================================================
# 5. SPLIT INPUT INTO EVENTS
# ============================================================

def split_events(sequence):

    if pd.isna(sequence):
        return []

    return [
        event.strip()
        for event in str(sequence).split("|")
        if event.strip()
    ]


final_test_df["events"] = final_test_df["input"].apply(
    split_events
)


# ============================================================
# 6. CHECK UNKNOWN EVENTS
# ============================================================

unknown_events = set()

for events in final_test_df["events"]:

    for event in events:

        if event not in event_to_id:

            unknown_events.add(event)


print("\n================================================")
print("UNKNOWN EVENTS IN FINAL TEST")
print("================================================")

if unknown_events:

    print(
        "Unknown event types:",
        len(unknown_events)
    )

    for event in sorted(unknown_events):

        print(repr(event))

else:

    print("No unknown events found.")


# ============================================================
# 7. CONVERT EVENTS → INTEGER IDs
# ============================================================

def events_to_ids(events):

    return [
        event_to_id.get(
            event,
            event_to_id["<UNK>"]
        )
        for event in events
    ]


final_test_df["event_ids"] = final_test_df["events"].apply(
    events_to_ids
)


# ============================================================
# 8. PAD SEQUENCES
# ============================================================

X_final = pad_sequences(
    final_test_df["event_ids"].tolist(),

    maxlen=MAX_LENGTH,

    padding="post",

    truncating="post",

    value=event_to_id["<PAD>"]
)


# ============================================================
# 9. GET ACTUAL LABELS
# ============================================================

y_final = final_test_df["label"].values


print("\n================================================")
print("FINAL TEST SHAPE")
print("================================================")

print("X_final:", X_final.shape)
print("y_final:", y_final.shape)


# ============================================================
# 10. LOAD TRAINED MODEL
# ============================================================

print("\n================================================")
print("LOADING TRAINED MODEL")
print("================================================")

model = load_model(MODEL_PATH)

print("Model loaded successfully.")
print("Model path:", MODEL_PATH)


# ============================================================
# 11. MAKE PREDICTIONS
# ============================================================

print("\n================================================")
print("GENERATING PREDICTIONS")
print("================================================")

probabilities = model.predict(
    X_final,
    verbose=1
)


# ============================================================
# 12. CONVERT PROBABILITY → CLASS
# ============================================================

predictions = (
    probabilities >= 0.5
).astype(int).flatten()


# ============================================================
# 13. FINAL RESULTS
# ============================================================

accuracy = accuracy_score(
    y_final,
    predictions
)

precision = precision_score(
    y_final,
    predictions,
    zero_division=0
)

recall = recall_score(
    y_final,
    predictions,
    zero_division=0
)

f1 = f1_score(
    y_final,
    predictions,
    zero_division=0
)


# ============================================================
# 14. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_final,
    predictions
)


print("\n================================================")
print("FINAL TEST RESULTS")
print("================================================")

print("\nConfusion Matrix:")
print(cm)

print("\nAccuracy :", accuracy)
print("Precision:", precision)
print("Recall   :", recall)
print("F1 Score :", f1)


# ============================================================
# 15. CLASSIFICATION REPORT
# ============================================================

print("\n================================================")
print("CLASSIFICATION REPORT")
print("================================================")

print(
    classification_report(
        y_final,
        predictions,
        target_names=[
            "Normal (0)",
            "Cheating (1)"
        ],
        zero_division=0
    )
)


# ============================================================
# 16. INDIVIDUAL PREDICTIONS
# ============================================================

print("\n================================================")
print("INDIVIDUAL PREDICTIONS")
print("================================================")

for i in range(len(final_test_df)):

    probability = float(probabilities[i][0])

    predicted_label = predictions[i]

    actual_label = y_final[i]

    predicted_class = (
        "CHEATING"
        if predicted_label == 1
        else "NORMAL"
    )

    actual_class = (
        "CHEATING"
        if actual_label == 1
        else "NORMAL"
    )

    print(
        f"Sample {i + 1:3} | "
        f"Actual: {actual_class:8} | "
        f"Predicted: {predicted_class:8} | "
        f"Probability: {probability:.4f}"
    )


# ============================================================
# 17. FINAL SUMMARY
# ============================================================

print("\n================================================")
print("FINAL SUMMARY")
print("================================================")

print("Total final test samples :", len(y_final))
print("Correct predictions      :", (y_final == predictions).sum())
print("Incorrect predictions    :", (y_final != predictions).sum())

print("\nAccuracy :", f"{accuracy:.4f}")
print("Precision:", f"{precision:.4f}")
print("Recall   :", f"{recall:.4f}")
print("F1 Score :", f"{f1:.4f}")


# ============================================================
# 18. SAVE FINAL TEST RESULTS TO FILE
# ============================================================

result_file = "../keystroke_dataset/gru_final_test_results.txt"


with open(result_file, "w", encoding="utf-8") as file:

    file.write("================================================\n")
    file.write("GRU FINAL TEST RESULTS\n")
    file.write("================================================\n\n")

    # Dataset information
    file.write(
        f"Total final test samples : {len(y_final)}\n"
    )

    file.write(
        f"Correct predictions      : {(y_final == predictions).sum()}\n"
    )

    file.write(
        f"Incorrect predictions    : {(y_final != predictions).sum()}\n"
    )

    file.write("\n")

    # Metrics
    file.write("Metrics:\n")
    file.write(
        f"Accuracy  : {accuracy:.4f}\n"
    )
    file.write(
        f"Precision : {precision:.4f}\n"
    )
    file.write(
        f"Recall    : {recall:.4f}\n"
    )
    file.write(
        f"F1 Score  : {f1:.4f}\n"
    )

    file.write("\n")

    # Confusion matrix
    file.write("================================================\n")
    file.write("CONFUSION MATRIX\n")
    file.write("================================================\n\n")

    file.write(
        str(cm)
    )

    file.write("\n\n")

    # Classification report
    file.write("================================================\n")
    file.write("CLASSIFICATION REPORT\n")
    file.write("================================================\n\n")

    file.write(
        classification_report(
            y_final,
            predictions,
            target_names=[
                "Normal (0)",
                "Cheating (1)"
            ],
            zero_division=0
        )
    )

    # Individual predictions
    file.write("\n================================================\n")
    file.write("INDIVIDUAL PREDICTIONS\n")
    file.write("================================================\n\n")

    for i in range(len(final_test_df)):

        probability = float(
            probabilities[i][0]
        )

        predicted_label = predictions[i]
        actual_label = y_final[i]

        predicted_class = (
            "CHEATING"
            if predicted_label == 1
            else "NORMAL"
        )

        actual_class = (
            "CHEATING"
            if actual_label == 1
            else "NORMAL"
        )

        file.write(
            f"Sample {i + 1:3} | "
            f"Actual: {actual_class:8} | "
            f"Predicted: {predicted_class:8} | "
            f"Probability: {probability:.4f}\n"
        )


print("\n================================================")
print("RESULTS SAVED")
print("================================================")

print("Results saved to:")
print(result_file)