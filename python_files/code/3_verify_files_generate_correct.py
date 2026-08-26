import os
import csv
import shutil

SOURCE_FOLDER = "../selected_keystrokes"
OUTPUT_FOLDER = "../corrected_keystrokes"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def get_encoding(path):
    """
    Try UTF-8 first, then cp1252.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.read()
        return "utf-8"
    except UnicodeDecodeError:
        return "cp1252"


def verify_file(file_path):
    """
    Verify the structure of a file.

    Returns:
        {
            "valid": bool,
            "rows": int,
            "three_column_rows": int,
            "nine_column_rows": int,
            "bad_rows": int,
            "bad_row_numbers": []
        }
    """

    encoding = get_encoding(file_path)

    result = {
        "valid": True,
        "rows": 0,
        "three_column_rows": 0,
        "nine_column_rows": 0,
        "bad_rows": 0,
        "bad_row_numbers": [],
        "encoding": encoding,
    }

    with open(
        file_path,
        "r",
        encoding=encoding,
        newline=""
    ) as infile:

        reader = csv.reader(infile, delimiter="\t")

        for line_number, row in enumerate(reader, start=1):

            # Skip completely empty rows
            if not row:
                continue

            result["rows"] += 1

            if len(row) == 3:
                result["three_column_rows"] += 1

            elif len(row) >= 9:
                result["nine_column_rows"] += 1

            else:
                result["bad_rows"] += 1
                result["bad_row_numbers"].append(line_number)
                result["valid"] = False

    return result


def correct_file(input_path, output_path):
    """
    Convert both supported formats into:

    PRESS_TIME    RELEASE_TIME    LETTER
    """

    encoding = get_encoding(input_path)

    with open(
        input_path,
        "r",
        encoding=encoding,
        newline=""
    ) as infile:

        reader = csv.reader(infile, delimiter="\t")

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
                "PRESS_TIME",
                "RELEASE_TIME",
                "LETTER"
            ])

            for line_number, row in enumerate(reader, start=1):

                if not row:
                    continue

                # --------------------------------
                # 3-column format
                # --------------------------------
                if len(row) == 3:

                    press_time = row[0].strip()
                    release_time = row[1].strip()
                    letter = row[2]

                # --------------------------------
                # 9-column format
                # --------------------------------
                elif len(row) >= 9:

                    press_time = row[5].strip()
                    release_time = row[6].strip()
                    letter = row[7]

                # --------------------------------
                # Unexpected format
                # --------------------------------
                else:

                    print(
                        f"  WARNING: Skipping malformed row "
                        f"{line_number}: {row}"
                    )

                    continue

                # Empty LETTER -> SPACE
                if letter is None or letter.strip() == "":
                    letter = "SPACE"

                writer.writerow([
                    press_time,
                    release_time,
                    letter
                ])


# ============================================================
# STEP 1: VERIFY ALL FILES
# ============================================================

print("=" * 70)
print("VERIFYING FILES")
print("=" * 70)

files = [
    filename
    for filename in os.listdir(SOURCE_FOLDER)
    if filename.endswith(".txt")
]

files.sort()

print(f"Total files found: {len(files)}\n")

valid_files = []
problem_files = []

total_rows = 0
total_3_column = 0
total_9_column = 0
total_bad_rows = 0


for index, filename in enumerate(files, start=1):

    file_path = os.path.join(SOURCE_FOLDER, filename)

    try:

        result = verify_file(file_path)

        total_rows += result["rows"]
        total_3_column += result["three_column_rows"]
        total_9_column += result["nine_column_rows"]
        total_bad_rows += result["bad_rows"]

        if result["valid"]:
            valid_files.append(filename)
        else:
            problem_files.append(filename)

        # Print files that contain the full 9-column format
        # or malformed rows
        if result["nine_column_rows"] > 0 or not result["valid"]:

            print(
                f"{filename}: "
                f"3-col={result['three_column_rows']}, "
                f"9-col={result['nine_column_rows']}, "
                f"bad={result['bad_rows']}"
            )

    except Exception as e:

        print(f"ERROR: {filename}: {e}")
        problem_files.append(filename)


# ============================================================
# VERIFICATION SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)

print(f"Total files:              {len(files)}")
print(f"Valid files:              {len(valid_files)}")
print(f"Problem files:            {len(problem_files)}")
print(f"Total rows:               {total_rows}")
print(f"3-column rows:            {total_3_column}")
print(f"9-column rows:            {total_9_column}")
print(f"Unexpected rows:          {total_bad_rows}")

if problem_files:
    print("\nProblem files:")

    for filename in problem_files:
        print(f"  - {filename}")

else:
    print("\nNo malformed files found.")


# ============================================================
# STEP 2: CORRECT ALL FILES
# ============================================================

print("\n" + "=" * 70)
print("CREATING CORRECTED FILES")
print("=" * 70)

processed = 0
failed = 0

for filename in files:

    input_path = os.path.join(SOURCE_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    try:

        correct_file(input_path, output_path)

        processed += 1

        if processed % 50 == 0:
            print(f"Processed {processed}/{len(files)} files...")

    except Exception as e:

        print(f"ERROR correcting {filename}: {e}")
        failed += 1


print("\n" + "=" * 70)
print("DONE")
print("=" * 70)

print(f"Files processed: {processed}")
print(f"Files failed:    {failed}")
print(f"Output folder:   {OUTPUT_FOLDER}")