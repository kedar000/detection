import os
import json
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

# Change this to your folder containing the JSON files
INPUT_FOLDER = Path("../cheating")


# ============================================================
# SPECIAL KEY MAPPING
# ============================================================

KEY_MAPPING = {
    # Modifier keys
    "Shift": "SHIFT",
    "Control": "CTRL",
    "Ctrl": "CTRL",
    "Alt": "ALT",
    "Meta": "WIN",
    "OS": "WIN",
    "CapsLock": "CAPS_LOCK",

    # Editing / navigation
    "Backspace": "BKSP",
    "Delete": "DELETE",
    "Insert": "INSERT",
    "Home": "HOME",
    "End": "END",
    "PageDown": "PG_DOWN",
    "PageUp": "PG_UP",

    # Enter / space
    "Enter": "ENTER",
    " ": "SPACE",
    "Space": "SPACE",

    # Arrow keys
    "ArrowUp": "ARW_UP",
    "ArrowDown": "ARw_DOWN",
    "ArrowLeft": "ARW_LEFT",
    "ArrowRight": "ARW_RIGHT",

    # Other keys
    "NumLock": "NUM_LK",
    "ContextMenu": "MENU",
}


# ============================================================
# CONVERT KEY
# ============================================================

def convert_key(key):
    """
    Convert browser KeyboardEvent key names into
    the required dataset representation.
    """

    # Special key
    if key in KEY_MAPPING:
        return KEY_MAPPING[key]

    # Already normalized special keys
    if key in {
        "SHIFT",
        "CTRL",
        "ALT",
        "WIN",
        "END",
        "BKSP",
        "HOME",
        "MENU",
        "NUM_1",
        "NUM_2",
        "NUM_4",
        "SPACE",
        "ARW_UP",
        "ARw_DOWN",
        "ARW_LEFT",
        "ARW_RIGHT",
        "DELETE",
        "INSERT",
        "NUM_LK",
        "CAPS_LOCK",
    }:
        return key

    # Everything else:
    # letters, numbers, punctuation, symbols, etc.
    return key


# ============================================================
# PROCESS ONE JSON FILE
# ============================================================

def process_file(file_path):
    """
    Read one JSON file, sort events, remove non-key events,
    and convert to TIME / MOVEMENT / LETTER format.
    """

    print(f"Processing: {file_path.name}")

    # --------------------------------------------------------
    # Read JSON
    # --------------------------------------------------------

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # --------------------------------------------------------
    # Make sure data is a list
    # --------------------------------------------------------

    if not isinstance(data, list):
        print(f"WARNING: {file_path.name} does not contain a JSON list.")
        return []

    # --------------------------------------------------------
    # Sort by timestamp ascending
    # --------------------------------------------------------

    data.sort(key=lambda x: x.get("timestamp", 0))

    # --------------------------------------------------------
    # Process events
    # --------------------------------------------------------

    output_rows = []

    for item in data:

        event = item.get("event", {})

        event_type = event.get("type")
        key = event.get("key")

        # ----------------------------------------------------
        # Keep ONLY keydown and keyup
        # ----------------------------------------------------

        if event_type not in ("keydown", "keyup"):
            continue

        # ----------------------------------------------------
        # Skip malformed events
        # ----------------------------------------------------

        if key is None:
            continue

        timestamp = item.get("timestamp")

        if timestamp is None:
            continue

        # ----------------------------------------------------
        # Convert movement
        # ----------------------------------------------------

        if event_type == "keydown":
            movement = "KEY_DOWN"
        else:
            movement = "KEY_UP"

        # ----------------------------------------------------
        # Convert key
        # ----------------------------------------------------

        letter = convert_key(key)

        # ----------------------------------------------------
        # Add row
        # ----------------------------------------------------

        output_rows.append(
            f"{timestamp}\t{movement}\t{letter}"
        )

    return output_rows


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Check folder
    # --------------------------------------------------------

    if not INPUT_FOLDER.exists():
        print(f"ERROR: Folder does not exist:")
        print(INPUT_FOLDER)
        return

    # --------------------------------------------------------
    # Get JSON files
    # --------------------------------------------------------

    json_files = sorted(
        [
            file
            for file in INPUT_FOLDER.iterdir()
            if file.is_file()
            and file.suffix.lower() == ".json"
        ]
    )

    if not json_files:
        print("No JSON files found.")
        return

    print(f"Found {len(json_files)} JSON files.")
    print()

    # --------------------------------------------------------
    # Process each file
    # --------------------------------------------------------

    for index, old_file in enumerate(json_files, start=1):

        # ----------------------------------------------------
        # Process original file
        # ----------------------------------------------------

        rows = process_file(old_file)

        # ----------------------------------------------------
        # New filename
        # ----------------------------------------------------

        new_file = INPUT_FOLDER / f"{index}_cheating.json"

        # ----------------------------------------------------
        # Write converted data
        # ----------------------------------------------------

        with open(new_file, "w", encoding="utf-8") as f:

            # Header
            f.write("TIME\tMOVEMENT\tLETTER\n")

            # Data
            for row in rows:
                f.write(row + "\n")

        # ----------------------------------------------------
        # Delete old file if name is different
        # ----------------------------------------------------

        if old_file.resolve() != new_file.resolve():
            old_file.unlink()

        print(
            f"  -> {new_file.name}: "
            f"{len(rows)} keyboard events"
        )

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()