"""
Description:
    Searches all keystroke files recursively and counts how many times
    each specified key is used.

    Both KEY_DOWN and KEY_UP are counted as one usage event.

    Example:
        KEY_DOWN(SHIFT) -> SHIFT count +1
        KEY_UP(SHIFT)   -> SHIFT count +1
"""

import os
import re
from collections import Counter

SOURCE_FOLDER = "../final_keystrokes"

TARGET_KEYS = [
    "ALT",
    "END",
    "WIN",
    "BKSP",
    "CTRL",
    "HOME",
    "MENU",
    "NUM_1",
    "NUM_2",
    "NUM_4",
    "SHIFT",
    "SPACE",
    "ARW_UP",
    "DELETE",
    "INSERT",
    "NUM_LK",
    "PG_DOWN",
    "ARw_DOWN",
    "ARW_DOWN",
    "ARW_LEFT",
    "ARW_RIGHT",
    "CAPS_LOCK",
]


# Make matching case-insensitive
target_keys_upper = {
    key.upper(): key
    for key in TARGET_KEYS
}

counts = Counter()
files_processed = 0


# ------------------------------------------------------------
# Search all folders recursively
# ------------------------------------------------------------

for root, dirs, files in os.walk(SOURCE_FOLDER):

    for filename in files:

        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(root, filename)

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as infile:

                for line in infile:

                    line = line.strip()

                    # Match:
                    # KEY_DOWN(SHIFT)
                    # KEY_UP(SHIFT)
                    match = re.match(
                        r"^(KEY_DOWN|KEY_UP)\((.*)\)$",
                        line
                    )

                    if not match:
                        continue

                    key = match.group(2).strip()

                    key_upper = key.upper()

                    if key_upper in target_keys_upper:
                        counts[key_upper] += 1

            files_processed += 1

        except Exception as e:

            print(f"Error reading {file_path}: {e}")


# ------------------------------------------------------------
# Print results
# ------------------------------------------------------------

print("=" * 60)
print("KEY USAGE COUNT")
print("=" * 60)

print(f"Files processed: {files_processed}")
print()

for key in TARGET_KEYS:

    print(
        f"{key:<12} : {counts[key.upper()]}"
    )

print("=" * 60)

print(f"TOTAL EVENTS: {sum(counts.values())}")