import os

PURGE_DIRS = ["clips", "compilation", "data"]
PROJECT_PATH = "projects"

file_list = []
for root, dirs, files in os.walk(PROJECT_PATH):
    for f in files:
        if ".mp4" == os.path.splitext(f)[1].lower():
            file_list.append(os.path.join(root, f))

for f in file_list:
    os.remove(f)
    print(f"{f} deleted..")
