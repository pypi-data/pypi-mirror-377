# Create and Write to a Text File
with open("Text.txt", "w") as f:
    f.write("Hello, this is the first line.\n")
    f.write("This is the second line.")
    print("Text file created and written.")
    
# Read from the Text File
with open("Text.txt", "r") as f:
    content = f.read()
    print("Content of the file:")
    print(content)

# Append to the Text File
with open("Text.txt", "a") as f:
    f.write("\nThis is an appended line")
    print("Text file appended")

# Read line by line
with open("Text.txt", "r") as f:
    for line in f:
        print(line.strip())
    
# File Pointer
with open("Text.txt", "r") as f:
    print("Position:", f.tell())
    print(f.read(10))
    print("After reading 10 chars:", f.tell())
    f.seek(5)
    print("Reset pointer:", f.tell())
    print(f.read(10))
    
# Check, Delete, Rename Files
import os
print("Exists:", os.path.exists("Text.txt"))
if os.path.exists("Text.txt"):
    os.rename("Text.txt", "renamed_Text.txt")
    print("Renamed to 'renamed_Text.txt'")

# Create Directory + File Inside
folder = "new_folder"
os.makedirs(folder, exist_ok=True)
with open(f"{folder}/nested.txt", "w") as f:
    f.write("This file is inside a folder")
    print("Folder and file created")

# List Files in a Directory
print("Files and folders in current dir:", os.listdir("."))

# Write to CSV
import csv
data = [["Name", "Age"], ["Alice", 25], ["Bob", 30]]
with open("people.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(data)
    print("CSV file written")

# Read from CSV
with open("people.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)

# Write to JSON
import json
info = {"name": "John", "age": 15, "hobbies": ["Cricket", "Batminton"]}
with open("data.json", "w") as f:
    json.dump(info, f, indent=4)
    print("JSON file created.")
    
# Read from JSON
with open("data.json", "r") as f:
    data = json.load(f)
    print("JSON content:", data)
    
# Read & Write Binary Files
source = "image.png"
target = "copied_image.jpg"
if os.path.exists(source):
    with open(source, "rb") as src_file:
        with open(target, "wb") as dst_file:
            dst_file.write(src_file.read())
            print("Binary file copied.")
else:
    print("Source image not found")
    
# Recursive File Search
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".txt"):
            print("Found:", os.path.join(root, file))

# Write, Read File Using Pathlib
from pathlib import Path
file = Path("pathlib_Text.txt")
file.write_text("This is written using pathlib")
print("..", file.read_text())
