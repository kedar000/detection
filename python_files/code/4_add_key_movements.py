"""
Description:
    Converts keystroke data from corrected_keystrokes into a temporal
    key-movement event format.

    Input columns:
        PRESS_TIME, RELEASE_TIME, LETTER

    Output columns:
        TIME, MOVEMENT, LETTER

    Each keystroke generates two events:
        PRESS_TIME   -> KEY_DOWN
        RELEASE_TIME -> KEY_UP

    All generated events within each file are sorted chronologically
    by TIME. This is important when a key such as SHIFT remains pressed
    while other keys are typed.

    Duplicate header rows are ignored and empty LETTER values are
    converted to SPACE.

    Input:
        ../corrected_keystrokes

    Output:
        ../Added_key_movements
"""

import os
import csv

SOURCE_FOLDER = "../corrected_keystrokes"
OUTPUT_FOLDER = "../Added_key_movements"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def is_header_row(row):
    """Check whether a row is a header row."""

    if len(row) < 3:
        return False

    return (
        row[0].strip().upper() == "PRESS_TIME"
        and row[1].strip().upper() == "RELEASE_TIME"
        and row[2].strip().upper() == "LETTER"
    )


def is_valid_data_row(row):
    """Check whether a row contains valid keystroke data."""

    if len(row) < 3:
        return False

    if is_header_row(row):
        return False

    press_time = row[0].strip()
    release_time = row[1].strip()

    if not press_time or not release_time:
        return False

    # Make sure timestamps are numeric
    try:
        int(press_time)
        int(release_time)
    except ValueError:
        return False

    return True


def process_file(input_path, output_path):

    events = []

    rows_read = 0
    duplicate_headers = 0
    invalid_rows = 0

    with open(
        input_path,
        "r",
        encoding="utf-8",
        newline=""
    ) as infile:

        reader = csv.reader(infile, delimiter="\t")

        for line_number, row in enumerate(reader, start=1):

            rows_read += 1

            # --------------------------------------------
            # Ignore duplicate headers
            # --------------------------------------------

            if is_header_row(row):
                duplicate_headers += 1
                continue

            # --------------------------------------------
            # Ignore malformed rows
            # --------------------------------------------

            if not is_valid_data_row(row):

                invalid_rows += 1

                print(
                    f"  WARNING: {os.path.basename(input_path)} "
                    f"line {line_number} skipped: {row}"
                )

                continue

            # --------------------------------------------
            # Extract data
            # --------------------------------------------

            press_time = int(row[0].strip())
            release_time = int(row[1].strip())

            letter = row[2]

            # Empty letter -> SPACE
            if letter.strip() == "":
                letter = "SPACE"

            # --------------------------------------------
            # Create KEY_DOWN event
            # --------------------------------------------

            events.append({
                "time": press_time,
                "movement": "KEY_DOWN",
                "letter": letter
            })

            # --------------------------------------------
            # Create KEY_UP event
            # --------------------------------------------

            events.append({
                "time": release_time,
                "movement": "KEY_UP",
                "letter": letter
            })

    # ====================================================
    # SORT ALL EVENTS BY TIME
    # ====================================================

    events.sort(key=lambda event: event["time"])

    # ====================================================
    # WRITE OUTPUT
    # ====================================================

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as outfile:

        writer = csv.writer(
            outfile,
            delimiter="\t",
            lineterminator="\n"
        )

        writer.writerow([
            "TIME",
            "MOVEMENT",
            "LETTER"
        ])

        for event in events:

            writer.writerow([
                event["time"],
                event["movement"],
                event["letter"]
            ])

    return {
        "rows_read": rows_read,
        "events_written": len(events),
        "duplicate_headers": duplicate_headers,
        "invalid_rows": invalid_rows
    }


# ============================================================
# PROCESS ALL FILES
# ============================================================

files = sorted(
    filename
    for filename in os.listdir(SOURCE_FOLDER)
    if filename.endswith(".txt")
)

print("=" * 70)
print("ADDING KEY MOVEMENTS")
print("=" * 70)

print(f"Input folder:  {SOURCE_FOLDER}")
print(f"Output folder: {OUTPUT_FOLDER}")
print(f"Files found:   {len(files)}")
print()


total_rows_read = 0
total_events_written = 0
total_duplicate_headers = 0
total_invalid_rows = 0

processed_files = 0
failed_files = 0


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

        result = process_file(
            input_path,
            output_path
        )

        total_rows_read += result["rows_read"]
        total_events_written += result["events_written"]
        total_duplicate_headers += result["duplicate_headers"]
        total_invalid_rows += result["invalid_rows"]

        processed_files += 1

        print(
            f"[{index}/{len(files)}] "
            f"{filename} -> "
            f"{result['events_written']} events"
        )

    except Exception as e:

        failed_files += 1

        print(
            f"[ERROR] {filename}: {e}"
        )


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("DONE")
print("=" * 70)

print(f"Files processed:       {processed_files}")
print(f"Files failed:          {failed_files}")
print(f"Rows read:             {total_rows_read}")
print(f"Events generated:      {total_events_written}")
print(f"Duplicate headers:     {total_duplicate_headers}")
print(f"Invalid rows skipped:  {total_invalid_rows}")

print()
print(f"Output folder: {OUTPUT_FOLDER}")