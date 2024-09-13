addon_name = "render_preset"
dirs_exclude = [
    ".git",
    ".github",
    "__pycache__",
    "releases",
    "resources",
]
file_pattern_exclude = [
    ".gitignore",
    ".ffs_db",
    ".build",
]
deploy_path = "/home/tonton/.config/blender/4.2/extensions/user_default/render_preset/"

import os, zipfile, shutil, sys

### CHECK BEHAVIOR (deploy/release)
# Missing argument
if len(sys.argv) == 1 :
    print("Missing argument")
    exit()

# Behavior selection
behavior = ""
if sys.argv[1].lower() in ["-rd", "-dr"]:
    behavior = "rd"
elif sys.argv[1].lower() == "-d":
    behavior = "d"
elif sys.argv[1].lower() == "-r":
    behavior = "r"

# Invalid argument
else:
    print("Invalid argument")
    exit()

### GET ADDON ROOTPATH
rootpath = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)
print(f"Rootpath : {rootpath}")

### GET VERSION
manifest_file = os.path.join(rootpath, "blender_manifest.toml")
with open(manifest_file) as file:
    for line in file:
        if line.startswith("version = "):
            version = line.split('"')[1]
            version = version.replace(".", "_")
print(f"Version : {version}")

### CREATE RELEASE/DEPLOY
release_path = os.path.join(os.path.join(rootpath, "releases"), f"{addon_name}_{version}.zip")

# Remove file if existing
if os.path.isfile(release_path):
    os.remove(release_path)
    print(f"Removed file : {release_path}")

# Get file list
file_list = []
for dirname, subdirs, files in os.walk(rootpath):
    for filename in files:

        # Exclude subdirs
        dir_components = dirname.split(os.sep)
        if len([x for x in dirs_exclude if x in dir_components])!=0:
            continue

        # Exclude files
        if len([x for x in file_pattern_exclude if x in filename])!=0:
            continue

        file_list.append(os.path.join(dirname, filename))

print("Files to treat :")
print(file_list)

# Create archive and deploy
if "r" in behavior:
    zipf = zipfile.ZipFile(release_path, "w")

for filepath in file_list:

    # Write to zip
    if "r" in behavior:
        zipf.write(
            filepath,
            os.path.basename(filepath), # Remove dir structure in zip
            )

    # Deploy
    if "d" in behavior:
        shutil.copy(
            filepath,
            deploy_path,
        )

# Recap
print()
if "r" in behavior:
    zipf.close()
    print(f"Release created : {release_path}")

if "d" in behavior:
    print(f"Deploy done in : {deploy_path}")

