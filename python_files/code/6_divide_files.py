"""
Description:
    Splits the final keystroke files into two datasets:

    50% -> original_50
    50% -> modify_50

    Files are randomly shuffled before splitting so that both datasets
    contain a representative random selection.

    The original files are not modified or deleted.

    A test dataset can be generated later from these two folders after
    the modification process is complete.
"""

import os
import random
import shutil

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

SOURCE_FOLDER = "../final_keystrokes"
OUTPUT_FOLDER = "../keystroke_dataset"

ORIGINAL_FOLDER = os.path.join(
    OUTPUT_FOLDER,
    "original_50"
)

MODIFY_FOLDER = os.path.join(
    OUTPUT_FOLDER,
    "modify_50"
)


# ------------------------------------------------------------
# Create output folders
# ------------------------------------------------------------

os.makedirs(ORIGINAL_FOLDER, exist_ok=True)
os.makedirs(MODIFY_FOLDER, exist_ok=True)


# ------------------------------------------------------------
# Get files
# ------------------------------------------------------------

files = [
    filename
    for filename in os.listdir(SOURCE_FOLDER)
    if filename.endswith(".txt")
]

print("=" * 60)
print("DATASET SPLIT")
print("=" * 60)

print(f"Total files: {len(files)}")


# ------------------------------------------------------------
# Shuffle files
# ------------------------------------------------------------

# Fixed seed makes the split reproducible.
random.seed(42)
random.shuffle(files)


# ------------------------------------------------------------
# Calculate split sizes
# ------------------------------------------------------------

total = len(files)

original_count = total // 2
modify_count = total - original_count


# ------------------------------------------------------------
# Split
# ------------------------------------------------------------

original_files = files[:original_count]

modify_files = files[original_count:]


# ------------------------------------------------------------
# Copy files
# ------------------------------------------------------------

def copy_files(file_list, destination):

    for filename in file_list:

        source_path = os.path.join(
            SOURCE_FOLDER,
            filename
        )

        destination_path = os.path.join(
            destination,
            filename
        )

        shutil.copy2(
            source_path,
            destination_path
        )


print("\nCopying original 50%...")
copy_files(
    original_files,
    ORIGINAL_FOLDER
)

print("Copying modify 50%...")
copy_files(
    modify_files,
    MODIFY_FOLDER
)


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("SPLIT COMPLETE")
print("=" * 60)

print(f"Original 50%: {len(original_files)} files")
print(f"Modify 50%:   {len(modify_files)} files")

print("\nOutput structure:")
print(OUTPUT_FOLDER)
print("├── original_50")
print("└── modify_50")