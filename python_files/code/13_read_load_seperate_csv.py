"""
GRU Dataset Preprocessing
=========================

Purpose:
    Prepare the keystroke event CSV files for GRU model training.

This script:
    1. Loads the training and test CSV files.
    2. Splits each input sequence using "|" as the event separator.
    3. Creates a fixed vocabulary for all supported keyboard events.
    4. Creates IDs for special application events.
    5. Reserves:
           <PAD> = 0
           <UNK> = 1
    6. Converts event sequences into integer ID sequences.
    7. Uses the same fixed vocabulary for both training and test data.
    8. Reports events that are not present in the vocabulary.
    9. Does NOT remove rows containing unknown events.

The output of this step is:
    train_df["events"]
    train_df["event_ids"]

    test_df["events"]
    test_df["event_ids"]

The GRU is NOT trained in this script.
The next step will be sequence padding.
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