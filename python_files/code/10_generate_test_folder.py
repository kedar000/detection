"""
Description:
    Creates a test dataset by selecting 10% of the files from:

        original_50
        modified_cheating

    The selected files are copied into:

        test/
        ├── original_10/
        └── modified_cheating_10/

    The original source folders are not modified or deleted.

    A fixed random seed is used so the same files are selected
    every time the script is run with the same dataset.
"""

import os
import random
import shutil


# ============================================================
# PATHS
# ============================================================

BASE_FOLDER = "../keystroke_dataset"

ORIGINAL_SOURCE = os.path.join(
    BASE_FOLDER,
    "original_50"
)

MODIFIED_SOURCE = os.path.join(
    BASE_FOLDER,
    "modified_cheating"
)

TEST_FOLDER = os.path.join(
    BASE_FOLDER,
    "test"
)

ORIGINAL_TEST_FOLDER = os.path.join(
    TEST_FOLDER,
    "original_10"
)

MODIFIED_TEST_FOLDER = os.path.join(
    TEST_FOLDER,
    "modified_cheating_10"
)


# ============================================================
# CREATE TEST DIRECTORIES
# ============================================================

os.makedirs(
    ORIGINAL_TEST_FOLDER,
    exist_ok=True
)

os.makedirs(
    MODIFIED_TEST_FOLDER,
    exist_ok=True
)


# ============================================================
# RANDOM SEED
# ============================================================

random.seed(42)


# ============================================================
# GET FILES
# ============================================================

def get_files(folder):

    return [
        filename
        for filename in os.listdir(folder)
        if filename.endswith(".txt")
    ]


original_files = get_files(
    ORIGINAL_SOURCE
)

modified_files = get_files(
    MODIFIED_SOURCE
)


# ============================================================
# CALCULATE 10%
# ============================================================

original_test_count = max(
    1,
    int(len(original_files) * 0.10)
)

modified_test_count = max(
    1,
    int(len(modified_files) * 0.10)
)


# ============================================================
# RANDOMLY SELECT TEST FILES
# ============================================================

original_test_files = random.sample(
    original_files,
    original_test_count
)

modified_test_files = random.sample(
    modified_files,
    modified_test_count
)


# ============================================================
# COPY FILES
# ============================================================

def copy_files(
    files,
    source_folder,
    destination_folder
):

    for filename in files:

        source_path = os.path.join(
            source_folder,
            filename
        )

        destination_path = os.path.join(
            destination_folder,
            filename
        )

        shutil.copy2(
            source_path,
            destination_path
        )


print("=" * 70)
print("CREATING TEST DATASET")
print("=" * 70)


print("\nCopying original test files...")

copy_files(
    original_test_files,
    ORIGINAL_SOURCE,
    ORIGINAL_TEST_FOLDER
)


print("Copying modified cheating test files...")

copy_files(
    modified_test_files,
    MODIFIED_SOURCE,
    MODIFIED_TEST_FOLDER
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("TEST DATASET CREATED")
print("=" * 70)

print(
    f"Original source files:          {len(original_files)}"
)

print(
    f"Original test files (10%):      {len(original_test_files)}"
)

print(
    f"Modified source files:          {len(modified_files)}"
)

print(
    f"Modified test files (10%):      {len(modified_test_files)}"
)

print("\nOutput structure:")

print(
    f"""
{TEST_FOLDER}/
├── original_10/
│   └── {len(original_test_files)} files
│
└── modified_cheating_10/
    └── {len(modified_test_files)} files
"""
)