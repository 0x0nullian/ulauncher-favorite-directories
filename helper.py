#!/usr/bin/env python3
import json
import os

def add_directory():
    extension_dir = os.path.expanduser("~/.local/share/ulauncher/extensions/com.github.0x0nullian.ulauncher-favorite-directories/")
    json_path = os.path.join(extension_dir, "directories.json")
    
    # Read existing directories
    with open(json_path, 'r') as f:
        directories = json.load(f)
    
    # Get new directory info
    keyword = input("Enter keyword (e.g., 'photos'): ")
    path = input("Enter full path: ")
    desc = input("Enter description (optional): ")
    
    # Add new entry
    directories.append({
        "keyword": keyword,
        "path": path,
        "description": desc or path
    })
    
    # Save back to file
    with open(json_path, 'w') as f:
        json.dump(directories, f, indent=4)
    
    print(f"Added '{keyword}' -> '{path}'")
    print("Restart Ulauncher or reload the extension to see changes.")

if __name__ == "__main__":
    add_directory()
