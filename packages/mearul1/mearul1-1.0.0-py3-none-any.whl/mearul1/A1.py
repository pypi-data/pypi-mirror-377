
#write
with open("Text.txt", "w") as f:
    f.write("Hello first line\n")
    f.write("second line")
    print("created nd written.")
 
# Read   
with open("Text.txt", "r") as f:
    content = f.read()
    print("Content of the file:")
    print(content)

# Append 
with open("Text.txt", "a") as f:
    f.write("\n appended line")
    print("file appended")

# Read line 
with open("Text.txt", "r") as f:
    for line in f:
        print(line.strip())
    
# Pointer
with open("Text.txt", "r") as f:
    print("Position:", f.tell())
    print(f.read(10))
    print("reading 10 chars:", f.tell())
    f.seek(5)
    print("Reset pointer:", f.tell())
    print(f.read(10))
    
# Delete Renme Files
import os
print("Exists:", os.path.exists("Text.txt"))
if os.path.exists("Text.txt"):
    os.rename("Text.txt", "renamed_Text.txt")
    print("Renamed 'renamed_Text.txt'")

# Create Directory
folder = "new_folder"
os.makedirs(folder, exist_ok=True)
with open(f"{folder}/nested.txt", "w") as f:
    f.write("File inside a folder")
    print("Folder nd file created")

# List File
print("Files nd folders in current dir:", os.listdir("."))

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

# Write JSON
import json
info = {"name": "John", "age": 15, "hobbies": ["Cricket", "Batminton"]}
with open("data.json", "w") as f:
    json.dump(info, f, indent=4)
    print("JSON file created.")
    
# Read JSON
with open("data.json", "r") as f:
    data = json.load(f)
    print("JSON content:", data)
    
# Read Write Binary
source = "image.png"
target = "C_image.jpg"
if os.path.exists(source):
    with open(source, "rb") as src_file:
        with open(target, "wb") as dst_file:
            dst_file.write(src_file.read())
            print("Binary file copied.")
else:
    print("Source image not found")
    
# Recursive File
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".txt"):
            print("Found:", os.path.join(root, file))

# Write Read File Using Pathlib
from pathlib import Path
file = Path("pathlib_Text.txt")
file.write_text("written using pathlib")
print("..", file.read_text())
