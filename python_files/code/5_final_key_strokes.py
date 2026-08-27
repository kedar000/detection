"""
Description:
    Converts timestamped keyboard events into a compact sequence format.

    Input:
        TIME    MOVEMENT    LETTER

    Output:
        MOVEMENT(LETTER)

    Example:
        1472173721269  KEY_DOWN  SHIFT
        1472173721439  KEY_DOWN  T
        1472173721569  KEY_UP    T
        1472173721686  KEY_UP    SHIFT

    Becomes:
        KEY_DOWN(SHIFT)
        KEY_DOWN(T)
        KEY_UP(T)
        KEY_UP(SHIFT)

    Events are sorted by TIME before being written.
"""

import os
import csv

SOURCE_FOLDER = "../Added_key_movements"
OUTPUT_FOLDER = "../final_keystrokes"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def is_header(row):
    """Check for the header row."""

    if len(row) < 3:
        return False

    return (
        row[0].strip().upper() == "TIME"
        and row[1].strip().upper() == "MOVEMENT"
        and row[2].strip().upper() == "LETTER"
    )


def process_file(input_path, output_path):

    events = []

    with open(
        input_path,
        "r",
        encoding="utf-8",
        newline=""
    ) as infile:

        reader = csv.reader(
            infile,
            delimiter="\t"
        )

        for line_number, row in enumerate(reader, start=1):

            # Ignore empty rows
            if not row:
                continue

            # Ignore duplicate headers
            if is_header(row):
                continue

            # Need at least TIME, MOVEMENT, LETTER
            if len(row) < 3:
                print(
                    f"WARNING: {os.path.basename(input_path)} "
                    f"line {line_number} skipped: {row}"
                )
                continue

            time = row[0].strip()
            movement = row[1].strip()
            letter = row[2]

            # Validate timestamp
            try:
                time = int(time)
            except ValueError:
                print(
                    f"WARNING: {os.path.basename(input_path)} "
                    f"line {line_number} has invalid TIME: {time}"
                )
                continue

            # Store event for sorting
            events.append(
                (time, movement, letter)
            )

    # ------------------------------------------------
    # Sort based on timestamp
    # ------------------------------------------------

    events.sort(key=lambda event: event[0])

    # ------------------------------------------------
    # Write final format
    # ------------------------------------------------

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as outfile:

        for time, movement, letter in events:

            outfile.write(
                f"{movement}({letter})\n"
            )


# ====================================================
# PROCESS ALL FILES
# ====================================================

files = sorted(
    filename
    for filename in os.listdir(SOURCE_FOLDER)
    if filename.endswith(".txt")
)

print("=" * 60)
print("CONVERTING KEYSTROKE EVENTS")
print("=" * 60)

print(f"Input folder:  {SOURCE_FOLDER}")
print(f"Output folder: {OUTPUT_FOLDER}")
print(f"Files found:   {len(files)}")
print()


processed = 0
failed = 0


for index, filename in enumerate(files, start=1):

    input_path = os.path.join(
        SOURCE_FOLDER,
        filename
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    try:

        process_file(
            input_path,
            output_path
        )

        processed += 1

        print(
            f"[{index}/{len(files)}] {filename}"
        )

    except Exception as e:

        failed += 1

        print(
            f"[ERROR] {filename}: {e}"
        )


print()
print("=" * 60)
print("DONE")
print("=" * 60)

print(f"Processed: {processed}")
print(f"Failed:    {failed}")
print(f"Output:    {OUTPUT_FOLDER}")