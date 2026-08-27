"""
Description:
    Iterates through all keystroke files, collects every unique key/letter
    used in the dataset, and generates a compact string containing those
    characters.

    Expected input format:
        KEY_DOWN(a)
        KEY_UP(a)
        KEY_DOWN(SHIFT)
        KEY_UP(SHIFT)

    Output:
        - Number of unique keys
        - List of unique keys
        - A compact character string containing printable characters
"""

import os
import re

SOURCE_FOLDER = "../final_keystrokes"

# Store unique keys
unique_keys = set()

files_processed = 0


# ------------------------------------------------------------
# Process all files
# ------------------------------------------------------------

files = [
    filename
    for filename in os.listdir(SOURCE_FOLDER)
    if filename.endswith(".txt")
]

for filename in files:

    file_path = os.path.join(
        SOURCE_FOLDER,
        filename
    )

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as infile:

            for line in infile:

                line = line.strip()

                if not line:
                    continue

                # Match:
                # KEY_DOWN(a)
                # KEY_UP(SHIFT)
                match = re.match(
                    r"^(KEY_DOWN|KEY_UP)\((.*)\)$",
                    line
                )

                if not match:
                    continue

                key = match.group(2)

                unique_keys.add(key)

        files_processed += 1

    except Exception as e:

        print(
            f"Error processing {filename}: {e}"
        )


# ------------------------------------------------------------
# Sort keys
# ------------------------------------------------------------

sorted_keys = sorted(
    unique_keys,
    key=lambda x: (
        len(x),
        x.lower()
    )
)


# ------------------------------------------------------------
# Generate character string
# ------------------------------------------------------------

# Printable single-character keys
characters = [
    key
    for key in sorted_keys
    if len(key) == 1 and key.isprintable()
]

character_string = "".join(characters)


# ------------------------------------------------------------
# Output
# ------------------------------------------------------------

print("=" * 60)
print("KEY USAGE ANALYSIS")
print("=" * 60)

print(f"Files processed: {files_processed}")
print(f"Unique keys:     {len(unique_keys)}")

print("\nUnique keys:")
print(sorted_keys)

print("\nCharacter string:")
print(character_string)

print("\nCharacter count:")
print(len(character_string))