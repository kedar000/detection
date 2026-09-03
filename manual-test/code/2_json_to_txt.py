from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FOLDER = Path("../cheating")


# ============================================================
# CONVERT JSON -> TXT AND DELETE JSON
# ============================================================

def convert_json_to_txt(folder):

    json_files = sorted(folder.glob("*.json"))

    if not json_files:
        print("No JSON files found.")
        return

    print(f"Found {len(json_files)} JSON files.\n")

    for json_file in json_files:

        # Create TXT filename
        txt_file = json_file.with_suffix(".txt")

        try:
            # Read JSON file as plain text
            with open(json_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Write TXT file
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(content)

            # Delete original JSON
            json_file.unlink()

            print(f"Converted and deleted: {json_file.name}")
            print(f"Created: {txt_file.name}\n")

        except Exception as e:
            print(f"ERROR processing {json_file.name}: {e}")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    convert_json_to_txt(INPUT_FOLDER)