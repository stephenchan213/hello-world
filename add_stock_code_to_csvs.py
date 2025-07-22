import csv
import os
import re
from glob import glob

# Pattern for your CSV files (adjust folder as needed)
folder_path = '.'  # Current directory
file_pattern = os.path.join(folder_path, 'output*.csv')

for filename in glob(file_pattern):
    # Extract stock code using regex (adjust pattern if needed)
    match = re.search(r'output(\d+)\.csv', os.path.basename(filename))
    if not match:
        print(f"Skipping {filename}: stock code not found in filename.")
        continue
    stock_code = match.group(1)
    
    # Read the original CSV file
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
    
    if not rows:
        print(f"Skipping {filename}: file is empty.")
        continue

    # Insert 'Stock Code' in header and stock_code in each row
    header = ['Stock Code'] + rows[0]
    data_rows = [[stock_code] + row for row in rows[1:]]
    output_rows = [header] + data_rows

    # Overwrite the original file
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(output_rows)
    
    print(f"Processed {filename}: stock code {stock_code} added as first column.")