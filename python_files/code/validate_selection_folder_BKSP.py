import os
import csv
import unicodedata

SOURCE_FOLDER = "../selected_keystrokes"

# Characters that are allowed even though they are technically control chars
ALLOWED_CONTROL_CHARS = {
    "\t",   # TSV delimiter
    "\n",   # newline
    "\r",   # Windows newline
}


def find_bad_characters(text):
    """
    Return suspicious/non-printable characters found in text.
    """

    bad_chars = []

    for char in text:

        # Unicode replacement character
        if char == "\ufffd":
            bad_chars.append(char)
            continue

        # Control / formatting characters
        category = unicodedata.category(char)

        if category.startswith("C") and char not in ALLOWED_CONTROL_CHARS:
            bad_chars.append(char)

    return bad_chars


def check_file(file_path):
    """
    Check the complete file for suspicious characters.
    """

    bad_characters = []

    # First verify that the file can be decoded
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

    except UnicodeDecodeError:
        return {
            "corrupted": True,
            "reason": "Invalid UTF-8 encoding",
            "characters": []
        }

    # Check for suspicious characters
    bad_characters = find_bad_characters(content)

    if bad_characters:
        unique_chars = list(dict.fromkeys(bad_characters))

        return {
            "corrupted": True,
            "reason": "Non-printable/control character",
            "characters": unique_chars
        }

    return {
        "corrupted": False,
        "reason": None,
        "characters": []
    }


# ============================================================
# SCAN FILES
# ============================================================

files = sorted(
    f for f in os.listdir(SOURCE_FOLDER)
    if f.endswith(".txt")
)

print("=" * 70)
print("CHECKING FOR CORRUPTED FILES")
print("=" * 70)

corrupted_files = []
valid_files = []

for filename in files:

    file_path = os.path.join(SOURCE_FOLDER, filename)

    result = check_file(file_path)

    if result["corrupted"]:

        corrupted_files.append(filename)

        print(f"\nCORRUPTED: {filename}")
        print(f"Reason: {result['reason']}")

        if result["characters"]:
            print("Characters:", end=" ")

            for char in result["characters"]:
                print(
                    f"U+{ord(char):04X}",
                    repr(char),
                    unicodedata.name(char, "UNKNOWN"),
                    end=" | "
                )

            print()

    else:
        valid_files.append(filename)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"Total files:     {len(files)}")
print(f"Valid files:     {len(valid_files)}")
print(f"Corrupted files: {len(corrupted_files)}")


# ============================================================
# DELETE CORRUPTED FILES
# ============================================================

if corrupted_files:

    print("\nDeleting corrupted files...")

    deleted = 0

    for filename in corrupted_files:

        file_path = os.path.join(SOURCE_FOLDER, filename)

        try:
            os.remove(file_path)
            deleted += 1
            print(f"Deleted: {filename}")

        except Exception as e:
            print(f"Could not delete {filename}: {e}")

    print(f"\nDeleted {deleted} corrupted files.")

else:
    print("\nNo corrupted files found.")