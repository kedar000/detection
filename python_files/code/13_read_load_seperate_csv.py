"""
============================================================
CURRENT SCRIPT SUMMARY
============================================================

This script prepares the training and validation datasets
for the GRU model.

Data flow:

    training_dataset.csv
            ↓
        train_df
            ↓
    Split into events
            ↓
    Fixed vocabulary
            ↓
    Events converted to integer IDs
            ↓
    Remove rows containing unknown events
            ↓
    Pad sequences to MAX_LENGTH = 3000
            ↓
        X_train, y_train


    test_dataset_training.csv
            ↓
         test_df
            ↓
    Same preprocessing
            ↓
        X_test, y_test

The test_use_for_final.csv file is NOT used in this script.
It will be loaded separately after the GRU model has been
completely trained for the final evaluation.

At the end of this script:

    X_train → padded training sequences
    y_train → training labels

    X_test  → padded validation sequences
    y_test  → validation labels

The GRU model has NOT been created or trained yet.

NEXT STEP:
    Build and configure the GRU model using X_train/y_train
    and validate it using X_test/y_test.
============================================================
"""

import pandas as pd
from tensorflow.keras.preprocessing.sequence import pad_sequences #python3 -m pip install tensorflow


# ============================================================
# 1. LOAD DATA
# ============================================================

train_df = pd.read_csv(
    "../keystroke_dataset/training_dataset.csv"
)

test_df = pd.read_csv(
    "../keystroke_dataset/test_dataset_training.csv"
)


print("Training samples:", len(train_df))
print("Test samples:", len(test_df))

print("\nTrain columns:", train_df.columns.tolist())
print("Test columns :", test_df.columns.tolist())


# ============================================================
# 2. SPLIT INPUT INTO EVENTS
# ============================================================

def split_events(sequence):
    """
    Convert:

        KEY_DOWN(SHIFT)|KEY_DOWN(A)|KEY_UP(A)

    into:

        [
            "KEY_DOWN(SHIFT)",
            "KEY_DOWN(A)",
            "KEY_UP(A)"
        ]

    Empty events are removed. This also handles a trailing "|".
    """

    if pd.isna(sequence):
        return []

    return [
        event.strip()
        for event in str(sequence).split("|")
        if event.strip()
    ]


train_df["events"] = train_df["input"].apply(split_events)
test_df["events"] = test_df["input"].apply(split_events)


# ============================================================
# 3. CREATE FIXED VOCABULARY
# ============================================================

event_to_id = {
    "<PAD>": 0,
    "<UNK>": 1
}


# ============================================================
# 4. PRINTABLE ASCII KEYBOARD CHARACTERS
# ============================================================
#
# ASCII 33 = !
# ASCII 126 = ~
#
# This includes:
#
# ! " # $ % & ' ( ) * + , - . /
# 0 1 2 3 4 5 6 7 8 9
# : ; < = > ? @
# A-Z
# [ \ ] ^ _ `
# a-z
# { | } ~
#
# Each character has:
#
# KEY_DOWN(character)
# KEY_UP(character)
# ============================================================

for ascii_code in range(33, 127):

    char = chr(ascii_code)

    down_event = f"KEY_DOWN({char})"
    up_event = f"KEY_UP({char})"

    event_to_id[down_event] = len(event_to_id)
    event_to_id[up_event] = len(event_to_id)


# ============================================================
# 5. SPECIAL KEYBOARD EVENTS
# ============================================================
#
# These names are based on the actual events found in your
# dataset.
# ============================================================

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


# ============================================================
# 6. APPLICATION / BROWSER EVENTS
# ============================================================

other_events = [
    "FOCUS_CHANGED",
    "VISIBILITY_CHANGED",
    "ANSWER_LENGTH_CHANGED",
]


for event in other_events:
    event_to_id[event] = len(event_to_id)


# ============================================================
# 7. CREATE REVERSE VOCABULARY
# ============================================================

id_to_event = {
    event_id: event
    for event, event_id in event_to_id.items()
}


# ============================================================
# 8. FIND UNKNOWN EVENTS
# ============================================================

def find_unknown_events(events):

    return [
        event
        for event in events
        if event not in event_to_id
    ]


train_df["unknown_events"] = train_df["events"].apply(
    find_unknown_events
)

test_df["unknown_events"] = test_df["events"].apply(
    find_unknown_events
)


# ============================================================
# 9. COLLECT UNIQUE UNKNOWN EVENTS
# ============================================================

unknown_events = set()

for events in train_df["unknown_events"]:
    unknown_events.update(events)

for events in test_df["unknown_events"]:
    unknown_events.update(events)


print("\n================================================")
print("UNKNOWN EVENTS")
print("================================================")

if unknown_events:

    for event in sorted(unknown_events):
        print(repr(event))

else:

    print("No unknown events found.")


# ============================================================
# 10. COUNT ROWS CONTAINING UNKNOWN EVENTS
# ============================================================

train_unknown_rows = (
    train_df["unknown_events"].str.len() > 0
).sum()

test_unknown_rows = (
    test_df["unknown_events"].str.len() > 0
).sum()


print("\nTraining rows with unknown events:",
      train_unknown_rows)

print("Test rows with unknown events:",
      test_unknown_rows)


# ============================================================
# 11. CONVERT EVENTS → INTEGER IDs
# ============================================================
#
# Known event:
#
#     KEY_DOWN(A) → some fixed number
#
# Unknown event:
#
#     unknown event → <UNK> → 1
#
# ============================================================

def events_to_ids(events):

    return [
        event_to_id.get(
            event,
            event_to_id["<UNK>"]
        )
        for event in events
    ]


train_df["event_ids"] = train_df["events"].apply(
    events_to_ids
)

test_df["event_ids"] = test_df["events"].apply(
    events_to_ids
)


# ============================================================
# 12. REMOVE TEMPORARY UNKNOWN-EVENT COLUMN
# ============================================================

train_df.drop(
    columns=["unknown_events"],
    inplace=True
)

test_df.drop(
    columns=["unknown_events"],
    inplace=True
)


# ============================================================
# 13. DISPLAY VOCABULARY
# ============================================================

print("\n================================================")
print("FIXED VOCABULARY")
print("================================================")

for event, event_id in event_to_id.items():

    print(f"{event_id:3} -> {event}")


# ============================================================
# 14. VOCABULARY SIZE
# ============================================================

print("\nVocabulary size:", len(event_to_id))


# ============================================================
# 15. DISPLAY TRAINING EXAMPLE
# ============================================================

print("\n================================================")
print("TRAINING EXAMPLE")
print("================================================")

print("\nOriginal input:")
print(train_df.iloc[0]["input"])

print("\nSeparated events:")
print(train_df.iloc[0]["events"])

print("\nInteger IDs:")
print(train_df.iloc[0]["event_ids"])

print("\nLabel:")
print(train_df.iloc[0]["label"])


# ============================================================
# 16. DISPLAY TEST EXAMPLE
# ============================================================

print("\n================================================")
print("TEST EXAMPLE")
print("================================================")

if len(test_df) > 0:

    print("\nOriginal input:")
    print(test_df.iloc[0]["input"])

    print("\nSeparated events:")
    print(test_df.iloc[0]["events"])

    print("\nInteger IDs:")
    print(test_df.iloc[0]["event_ids"])

    print("\nLabel:")
    print(test_df.iloc[0]["label"])

else:

    print("Test dataset is empty.")


# ============================================================
# 17. FINAL SUMMARY
# ============================================================

print("\n================================================")
print("FINAL SUMMARY")
print("================================================")

print("Training samples :", len(train_df))
print("Test samples     :", len(test_df))
print("Vocabulary size  :", len(event_to_id))
print("Unknown events   :", len(unknown_events))

# ============================================================

# 10. SAVE UNKNOWN EVENTS TO FILE

# ============================================================

unknown_events_file = "../keystroke_dataset/unknown_events.txt"

with open(unknown_events_file, "w", encoding="utf-8") as file:

    for event in sorted(unknown_events):

        file.write(repr(event) + "\n")

print("\nUnknown events saved to:")

print(unknown_events_file)



# ============================================================
# REMOVE ROWS CONTAINING UNKNOWN EVENTS
# ============================================================

# Keep only rows where there are NO unknown events
train_df = train_df[
    train_df["events"].apply(
        lambda events: all(event in event_to_id for event in events)
    )
].copy()

test_df = test_df[
    test_df["events"].apply(
        lambda events: all(event in event_to_id for event in events)
    )
].copy()


# ============================================================
# PRINT LENGTH AFTER REMOVAL
# ============================================================

print("\n================================================")
print("DATASET AFTER REMOVING UNKNOWN EVENTS")
print("================================================")

print("Training samples:", len(train_df))
print("Test samples    :", len(test_df))


# ============================================================
# VERIFY THAT NO UNKNOWN EVENTS REMAIN
# ============================================================

remaining_train_unknown = set()

for events in train_df["events"]:
    for event in events:
        if event not in event_to_id:
            remaining_train_unknown.add(event)


remaining_test_unknown = set()

for events in test_df["events"]:
    for event in events:
        if event not in event_to_id:
            remaining_test_unknown.add(event)


print("\nRemaining unknown events in training:",
      remaining_train_unknown)

print("Remaining unknown events in test:",
      remaining_test_unknown)


# ============================================================
# 18. CHECK SEQUENCE LENGTHS
# ============================================================

train_lengths = train_df["event_ids"].apply(len)
test_lengths = test_df["event_ids"].apply(len)

print("\n================================================")
print("SEQUENCE LENGTHS")
print("================================================")

print("\nTraining:")
print("Minimum length :", train_lengths.min())
print("Maximum length :", train_lengths.max())
print("Average length :", train_lengths.mean())
print("Median length  :", train_lengths.median())

print("\nTest:")
print("Minimum length :", test_lengths.min())
print("Maximum length :", test_lengths.max())
print("Average length :", test_lengths.mean())
print("Median length  :", test_lengths.median())



# ============================================================
# 19. PAD / TRUNCATE SEQUENCES
# ============================================================



MAX_LENGTH = 3000
PAD_VALUE = event_to_id["<PAD>"]


# ============================================================
# Training sequences
# ============================================================

X_train = pad_sequences(
    train_df["event_ids"].tolist(),
    maxlen=MAX_LENGTH,
    padding="post",
    truncating="post",
    value=PAD_VALUE
)


# ============================================================
# Test sequences
# ============================================================

X_test = pad_sequences(
    test_df["event_ids"].tolist(),
    maxlen=MAX_LENGTH,
    padding="post",
    truncating="post",
    value=PAD_VALUE
)


# ============================================================
# Labels
# ============================================================

y_train = train_df["label"].values
y_test = test_df["label"].values


# ============================================================
# Check shapes
# ============================================================

print("\n================================================")
print("PADDED DATA")
print("================================================")

print("X_train shape:", X_train.shape)
print("y_train shape:", y_train.shape)

print("X_test shape :", X_test.shape)
print("y_test shape :", y_test.shape)


# ============================================================
# Check first sequence
# ============================================================

print("\nFirst training sequence:")
print(X_train[0])

print("\nOriginal sequence length:",
      len(train_df.iloc[0]["event_ids"]))

print("Padded sequence length:",
      len(X_train[0]))
# ============================================================
# 20. BUILD GRU MODEL
# ============================================================

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GRU, Dense, Dropout


VOCAB_SIZE = len(event_to_id)
EMBEDDING_DIM = 64
GRU_UNITS = 64


model = Sequential([

    Embedding(
        input_dim=VOCAB_SIZE,
        output_dim=EMBEDDING_DIM,
        mask_zero=True,
        input_shape=(MAX_LENGTH,)
    ),

    GRU(
        GRU_UNITS
    ),

    Dropout(0.3),

    Dense(
        32,
        activation="relu"
    ),

    Dropout(0.2),

    Dense(
        1,
        activation="sigmoid"
    )
])


# ============================================================
# 21. COMPILE MODEL
# ============================================================

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)


# ============================================================
# 22. DISPLAY MODEL
# ============================================================

print("\n================================================")
print("GRU MODEL")
print("================================================")

model.summary()

# ============================================================
# 23. TRAIN THE GRU MODEL
# ============================================================

from tensorflow.keras.callbacks import EarlyStopping


early_stopping = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)


print("\n================================================")
print("STARTING GRU TRAINING")
print("================================================")


history = model.fit(
    X_train,
    y_train,

    validation_data=(
        X_test,
        y_test
    ),

    epochs=30,
    batch_size=16,

    callbacks=[
        early_stopping
    ],

    verbose=1
)

# ============================================================
# SAVE TRAINED MODEL
# ============================================================

model_path = "../keystroke_dataset/gru_overlay_detection.keras"

model.save(model_path)

print("\nTrained model saved to:")
print(model_path)

# ============================================================
# 24. EVALUATE MODEL ON VALIDATION DATA
# ============================================================

print("\n================================================")
print("VALIDATION EVALUATION")
print("================================================")

val_loss, val_accuracy = model.evaluate(
    X_test,
    y_test,
    verbose=1
)

print("\nValidation Loss    :", val_loss)
print("Validation Accuracy:", val_accuracy)

# ============================================================
# 25. SAVE BEST MODEL
# ============================================================

best_model_path = "../keystroke_dataset/gru_overlay_detection_best.keras"

model.save(best_model_path)

print("\nBest model saved to:")
print(best_model_path)

# ============================================================
# 26. CONFUSION MATRIX + PRECISION + RECALL + F1-SCORE
# ============================================================

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score
)


print("\n================================================")
print("VALIDATION METRICS")
print("================================================")


# ------------------------------------------------------------
# Generate predictions
# ------------------------------------------------------------

y_val_probability = model.predict(
    X_test,
    verbose=0
)


# Convert probabilities to 0/1
y_val_pred = (
    y_val_probability >= 0.5
).astype(int).flatten()


# ------------------------------------------------------------
# Confusion Matrix
# ------------------------------------------------------------

cm = confusion_matrix(
    y_test,
    y_val_pred
)

print("\nConfusion Matrix:")
print(cm)


# ------------------------------------------------------------
# Precision
# ------------------------------------------------------------

precision = precision_score(
    y_test,
    y_val_pred,
    zero_division=0
)


# ------------------------------------------------------------
# Recall
# ------------------------------------------------------------

recall = recall_score(
    y_test,
    y_val_pred,
    zero_division=0
)


# ------------------------------------------------------------
# F1 Score
# ------------------------------------------------------------

f1 = f1_score(
    y_test,
    y_val_pred,
    zero_division=0
)


print("\nPrecision :", precision)
print("Recall    :", recall)
print("F1 Score  :", f1)


# ------------------------------------------------------------
# Complete classification report
# ------------------------------------------------------------

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_val_pred,
        target_names=[
            "Normal (0)",
            "Cheating (1)"
        ],
        zero_division=0
    )
)