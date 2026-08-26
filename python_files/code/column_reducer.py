import os
import csv

# column_reducer.py is inside:
# python_files/code/
#
# Therefore these paths are one level above.
SOURCE_FOLDER = "../selected_keystrokes"    #use verify_files_generator_correct
OUTPUT_FOLDER = "../processed_keystrokes"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

processed = 0
failed = 0

for filename in os.listdir(SOURCE_FOLDER):

    if not filename.endswith(".txt"):
        continue

    input_path = os.path.join(SOURCE_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    try:
        # cp1252 can read bytes such as 0xb4 that UTF-8 cannot.
        with open(input_path, "r", encoding="cp1252", newline="") as infile:

            reader = csv.DictReader(infile, delimiter="\t")

            # Check required columns
            if not reader.fieldnames:
                print(f"Skipping {filename}: no columns found")
                failed += 1
                continue

            required_columns = {"PRESS_TIME", "RELEASE_TIME", "LETTER"}

            if not required_columns.issubset(set(reader.fieldnames)):
                print(
                    f"Skipping {filename}: missing columns. "
                    f"Found: {reader.fieldnames}"
                )
                failed += 1
                continue

            with open(
                output_path,
                "w",
                encoding="utf-8",
                newline=""
            ) as outfile:

                writer = csv.writer(outfile, delimiter="\t")

                # Output header
                writer.writerow([
                    "PRESS_TIME",
                    "RELEASE_TIME",
                    "LETTER"
                ])

                for row in reader:

                    letter = row["LETTER"]

                    # Empty LETTER becomes SPACE
                    if letter is None or letter.strip() == "":
                        letter = "SPACE"

                    writer.writerow([
                        row["PRESS_TIME"],
                        row["RELEASE_TIME"],
                        letter
                    ])

        processed += 1

        if processed % 50 == 0:
            print(f"Processed {processed} files...")

    except Exception as e:
        print(f"Error processing {filename}: {e}")
        failed += 1


print("\nDone.")
print(f"Successfully processed: {processed}")
print(f"Failed/skipped: {failed}")
print(f"Output folder: {OUTPUT_FOLDER}")