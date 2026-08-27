"""
Description:
    Generates the final training and testing CSV datasets.

    Training:
        original_50          -> label 0
        modified_cheating   -> label 1

    Testing:
        test/original_10              -> label 0
        test/modified_cheating_10    -> label 1

    Each file becomes one row:
        input,label

    The input contains the complete keystroke event sequence
    from that file.

    Training samples are shuffled randomly so that normal and
    cheating samples are mixed instead of appearing as:

        all label 0
        all label 1
"""


import os
import csv
import random


# ============================================================
# PATHS
# ============================================================

BASE_FOLDER = "../keystroke_dataset"

ORIGINAL_TRAIN_FOLDER = os.path.join(
    BASE_FOLDER,
    "original_50"
)

MODIFIED_TRAIN_FOLDER = os.path.join(
    BASE_FOLDER,
    "modified_cheating"
)

ORIGINAL_TEST_FOLDER = os.path.join(
    BASE_FOLDER,
    "test",
    "original_10"
)

MODIFIED_TEST_FOLDER = os.path.join(
    BASE_FOLDER,
    "test",
    "modified_cheating_10"
)


TRAIN_OUTPUT = os.path.join(
    BASE_FOLDER,
    "training_dataset.csv"
)

TEST_OUTPUT = os.path.join(
    BASE_FOLDER,
    "test_dataset.csv"
)


# ============================================================
# RANDOM SEED
# ============================================================

# Fixed seed makes the generated dataset reproducible.
random.seed(42)


# ============================================================
# READ FILES
# ============================================================

def read_dataset(folder, label):
    """
    Read all .txt files from a folder.

    Each file becomes one training/test sample.

    Returns:
        [
            {
                "input": "...",
                "label": 0
            },
            ...
        ]
    """

    samples = []

    files = sorted(
        filename
        for filename in os.listdir(folder)
        if filename.endswith(".txt")
    )

    for filename in files:

        file_path = os.path.join(
            folder,
            filename
        )

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as infile:

                # Read all events from the file
                events = [
                    line.strip()
                    for line in infile
                    if line.strip()
                ]

            # Skip empty files
            if not events:
                print(
                    f"WARNING: Empty file skipped: {file_path}"
                )
                continue

            # Join events into one input string
            #
            # Example:
            #
            # KEY_DOWN(H)|KEY_UP(H)|KEY_DOWN(e)|KEY_UP(e)
            #
            input_sequence = "|".join(events)

            samples.append({
                "input": input_sequence,
                "label": label
            })

        except Exception as e:

            print(
                f"ERROR reading {file_path}: {e}"
            )

    return samples


# ============================================================
# WRITE CSV
# ============================================================

def write_csv(samples, output_path):

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as outfile:

        writer = csv.writer(outfile)

        # Header
        writer.writerow([
            "input",
            "label"
        ])

        for sample in samples:

            writer.writerow([
                sample["input"],
                sample["label"]
            ])


# ============================================================
# GENERATE TRAINING DATASET
# ============================================================

print("=" * 70)
print("GENERATING TRAINING DATASET")
print("=" * 70)

original_train_samples = read_dataset(
    ORIGINAL_TRAIN_FOLDER,
    0
)

modified_train_samples = read_dataset(
    MODIFIED_TRAIN_FOLDER,
    1
)


# Combine normal + cheating
training_samples = (
    original_train_samples +
    modified_train_samples
)


# ------------------------------------------------------------
# IMPORTANT:
# Shuffle the combined dataset.
# This prevents:
#
# 0
# 0
# 0
# ...
# 1
# 1
# 1
#
# Instead, labels are mixed.
# ------------------------------------------------------------

random.shuffle(training_samples)


# Write training CSV
write_csv(
    training_samples,
    TRAIN_OUTPUT
)


# ============================================================
# GENERATE TEST DATASET
# ============================================================

print()
print("=" * 70)
print("GENERATING TEST DATASET")
print("=" * 70)

original_test_samples = read_dataset(
    ORIGINAL_TEST_FOLDER,
    0
)

modified_test_samples = read_dataset(
    MODIFIED_TEST_FOLDER,
    1
)


# Combine test samples
test_samples = (
    original_test_samples +
    modified_test_samples
)


# Shuffle test samples as well
random.shuffle(test_samples)


# Write test CSV
write_csv(
    test_samples,
    TEST_OUTPUT
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("DATASET GENERATION COMPLETE")
print("=" * 70)

print()
print("TRAINING DATASET")
print(f"  Original / label 0 : {len(original_train_samples)}")
print(f"  Modified / label 1 : {len(modified_train_samples)}")
print(f"  Total               : {len(training_samples)}")

print()
print("TEST DATASET")
print(f"  Original / label 0 : {len(original_test_samples)}")
print(f"  Modified / label 1 : {len(modified_test_samples)}")
print(f"  Total               : {len(test_samples)}")

print()
print(f"Training CSV: {TRAIN_OUTPUT}")
print(f"Test CSV:     {TEST_OUTPUT}")