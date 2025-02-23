# Description: This script is used to organize (move and rename) photos from BeReal downloaded data
# Searching images is based on the reading of a json file containing the path of the images: memories.json
# The script will move the images to a folder named "photos" and will rename them with the date of the memory
# The script will also create a text file containing the description of the memory 

import json
from datetime import datetime
from pathlib import Path
import shutil
import os

# Variables user should change
memories_json_file="BeReal_data/memories.json"

# Variables that should not be changed
# photos_folder is the folder where all the photos are stored
photos_folder=memories_json_file.split("/")[0]+"/Photos"


def find_file(filename, search_path="."):
    """
    Find a file in a folder and its subfolders
    return the absolute path of the file
    """
    search_path = Path(search_path)
    for file in search_path.rglob("*"):  # Find in every files and folders
        if filename in file.name:  # Verify if the name matches
            return file.resolve()  # Return absolute path
    return None

def get_unique_filename(base_path, filename):
    """
    Check if a file already exists and generate a unique name by adding a counter if necessary.
    """
    base_path = Path(base_path)
    file_path = base_path / filename
    name, ext = filename.rsplit(".", 1)  # Split the name and the extension
    counter = 1

    while file_path.exists():
        file_path = base_path / f"{name}_{counter}.{ext}"  # Format the new name
        counter += 1
    return str(file_path)

print("Organizing photos from BeReal data... This may take some time.")

# Create the folder where the photos will be stored
if not os.path.exists("photos"):
    os.makedirs("photos")
else:
    print("A folder named 'photos' already exists. Please delete it before running the script.")
    exit(1)

# For each entry of json file, get the date, rename the photo and move it to the correct folder
with open(memories_json_file) as f:
    data = json.load(f)
    
    # Get date, caption and the path of the front and back images for each memory
    for d in data:
        date = d["date"]
        if "caption" in d:
            caption = d["caption"]
        else:
            caption = ""
        
        front_image_path = d["frontImage"].get("path")
        back_image_path = d["backImage"].get("path")

        # Understand date string as date
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Change date format to "YYYY_MM_DD'"
        date = date.strftime("%Y_%m_%d")
        # Get the year
        year_taken=date.split("_")[0]
        
        # Get front and back files names
        front_image_name = front_image_path.split("/")[-1]
        back_image_name = back_image_path.split("/")[-1]
        
        # find the front_image_path file in photos_folder
        front_image_file_path = find_file(front_image_name, photos_folder)
        back_image_file_path = find_file(back_image_name, photos_folder)

        # Get the extension of the file, extensions can be different
        front_image_name_extension = front_image_name.split(".")[-1]
        back_image_name_extension = back_image_name.split(".")[-1]

        if not front_image_file_path:
            print(f"Warning: File {front_image_name} not found. Skipping this memory.")
            continue
        if not back_image_file_path:
            print(f"Warning: File {back_image_name} not found. Skipping this memory.")
            continue

        # Organize the photos
        # Create folder for the year if it does not exist
        if not os.path.exists("photos/"+year_taken):
            os.makedirs("photos/"+year_taken)

        new_file_name_front = date+"_front"
        new_file_name_back = date+"_back"

        # Copy front file to the new folder
        dest_file = get_unique_filename(f"photos/{year_taken}", f"{new_file_name_front}.{front_image_name_extension}")
        shutil.copyfile(front_image_file_path, dest_file)
        # Copy back file to the new folder
        dest_file = get_unique_filename(f"photos/{year_taken}", f"{new_file_name_back}.{back_image_name_extension}")
        shutil.copyfile(back_image_file_path, dest_file)

        # Create a text file with the caption if it exists
        if caption:
            caption_file = get_unique_filename(f"photos/{year_taken}", f"{date}_description.txt")
            with open(caption_file, "x") as file:
                file.write(caption)

print("Done! Photos organized in the folder 'photos'.")