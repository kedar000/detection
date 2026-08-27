"""
Description:
    Splits the final keystroke files into three datasets:

    45% -> original_45
    45% -> modify_45
    10% -> test_10

    Files are randomly shuffled before splitting so that each
    dataset contains a representative random selection.

    The original files are not modified or deleted.
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
    "original_45"
)

MODIFY_FOLDER = os.path.join(
    OUTPUT_FOLDER,
    "modify_45"
)

TEST_FOLDER = os.path.join(
    OUTPUT_FOLDER,
    "test_10"
)


# ------------------------------------------------------------
# Create output folders
# ------------------------------------------------------------

os.makedirs(ORIGINAL_FOLDER, exist_ok=True)
os.makedirs(MODIFY_FOLDER, exist_ok=True)
os.makedirs(TEST_FOLDER, exist_ok=True)


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

original_count = int(total * 0.45)
modify_count = int(total * 0.45)

# Everything remaining goes to test.
test_count = total - original_count - modify_count


# ------------------------------------------------------------
# Split
# ------------------------------------------------------------

original_files = files[:original_count]

modify_files = files[
    original_count:
    original_count + modify_count
]

test_files = files[
    original_count + modify_count:
]


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


print("\nCopying original 45%...")
copy_files(
    original_files,
    ORIGINAL_FOLDER
)

print("Copying modify 45%...")
copy_files(
    modify_files,
    MODIFY_FOLDER
)

print("Copying test 10%...")
copy_files(
    test_files,
    TEST_FOLDER
)


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("SPLIT COMPLETE")
print("=" * 60)

print(f"Original 45%: {len(original_files)} files")
print(f"Modify 45%:   {len(modify_files)} files")
print(f"Test 10%:     {len(test_files)} files")

print("\nOutput structure:")
print(OUTPUT_FOLDER)
print("├── original_45")
print("├── modify_45")
print("└── test_10")