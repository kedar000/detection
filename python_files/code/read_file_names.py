# read file names 
# import os

# folder_path = "/Users/kedarchinna/Desktop/Keystrokes/files"

# file_names = []

# with os.scandir(folder_path) as entries:
#     for entry in entries:
#         if entry.is_file():
#             file_names.append(entry.name)

#         if len(file_names) == 500:
#             break

# print(file_names)



import os
import shutil

source_folder = "/Users/kedarchinna/Desktop/Keystrokes/files"
destination_folder = "./selected_keystrokes"

# Create destination folder if it doesn't exist
os.makedirs(destination_folder, exist_ok=True)

count = 0

with os.scandir(source_folder) as entries:
    for entry in entries:
        if not entry.is_file():
            continue

        count += 1

        # Copy file as 1_keystroke, 2_keystroke, ...
        destination_path = os.path.join(
            destination_folder,
            f"{count}_keystroke{os.path.splitext(entry.name)[1]}"
        )

        shutil.copy2(entry.path, destination_path)

        if count == 500:
            break

print(f"Copied {count} files to: {destination_folder}")