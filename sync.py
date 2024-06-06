import os
import requests
import re

from typing import List

FAILED = []

def get_img_url_from_file(path: str) -> List[str]:
    with open(path, "r", encoding="UTF-8") as f:
        content = f.read()

    return (os.path.split(path)[0], re.findall(r"https?://[^\s]+(?:jpg|png)", content))

def get_files(repo_path: str) -> List[str]:
    files = []
    for root, dirs, filenames in os.walk(repo_path):
        for filename in filenames:
            if filename.endswith(".xaml") or filename.endswith(".md"):

                files.append(os.path.join(root, filename))
        for dirname in dirs:
            files.extend(get_files(os.path.join(root, dirname)))
    return files

def get_img(url: str):
    i = 0
    while True:
        try:
            return requests.get(url, timeout=10).content
        except:
            i += 1
            if i > 3:
                print(f"Failed to download image {url}, skipping...")
                FAILED.append(url)
                return None
            print(f"Failed to download image {url}, retrying...")

if __name__ == "__main__":
    # Get the list of files in the repository
    files = get_files("PCL2Help")

    print("Scanning files...")

    # Send the list of files to the server
    for file in files:
        dir_name, img_urls = get_img_url_from_file(file)
        print(f"Found {len(img_urls)} images in {file}")
        for img_url in img_urls:
            with open(os.path.join(dir_name, img_url.split("/")[-1]), "wb") as f:
                content = get_img(img_url)
                if content:
                    f.write(content)
                    print(f"Downloaded image {img_url}")
    print("Failed to download the following images:")
    for url in FAILED:
        print("    "+url)
    print("Done!")