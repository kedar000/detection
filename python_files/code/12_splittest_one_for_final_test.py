import pandas as pd

# Input CSV
input_file = "../keystroke_dataset/test_dataset.csv"

# Output files
output_file_1 = "../keystroke_dataset/test_use_for_final.csv"
output_file_2 = "../keystroke_dataset/test_dataset_training.csv"

# Read CSV
df = pd.read_csv(input_file)

# Find midpoint
mid = len(df) // 2

# Split into two halves
df1 = df.iloc[:mid]
df2 = df.iloc[mid:]

# Save
df1.to_csv(output_file_1, index=False)
df2.to_csv(output_file_2, index=False)

print(f"Total rows: {len(df)}")
print(f"Part 1: {len(df1)} rows")
print(f"Part 2: {len(df2)} rows")