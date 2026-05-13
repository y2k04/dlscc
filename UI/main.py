import os
import json
import urllib.request
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Define constants
USER_DIR = os.path.expanduser("~")
GITHUB_REPO_URL = "https://api.github.com/repos/y2k04/dlscc/contents"
PROJECTS_DIR = os.path.join(USER_DIR, "AppData", "LocalLow", "SebastianLague", "Digital Logic Sim", "V1", "Projects")
CHIP_FILE_EXT = ".json"
DE = []

def downlaodChip(chip, project):
    DE = []
    # first, remove the prefix of this and store it to a new var: "69F3A590_1B-REGISTER"
    prefix = chip.split("_")[0]
    # then, download the chip file from github and store it to a new var: chip-content github url https://raw.githubusercontent.com/y2k04/dlscc/repo/prefix/chip.json
    chip_content = requests.get(f"https://raw.githubusercontent.com/y2k04/dlscc/repo/{prefix}/{chip}.json")
    # save chip content to Projects dir / project 
    filename = os.path.join(PROJECTS_DIR, project, "CHIPS", chip.replace('69F3A590_', '') + CHIP_FILE_EXT)
    if chip_content.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(chip_content.content)
        with open(filename, "r+") as f:
            content = f.read()
            f.seek(0)  # move the file pointer to the beginning of the file
            f.write(content.replace('69F3A590_', ''))  # replace all instances of the string with an empty string    
            f.truncate()
        with open(filename, "r") as f:
            dependancies = json.load(f)
            for d in dependancies['Dependencies']:
                print(f'warning: dependancy{d} is required')
                DE.append("Warning: dependancy"+d+" is required")
                f.seek(0)
    else:
        print(f"Failed to download file from {chip_content.url}")
        return False
    settings_file = os.path.join(PROJECTS_DIR, project, "ProjectSettings.json")
    if not os.path.exists(settings_file):
        print(f"Project settings file not found: {settings_file}")
        exit()

    with open(settings_file, "r+") as f:
        settings = json.load(f)
        if "AllCreatedChips" not in settings:
            settings["AllCreatedChips"] = []
        settings["AllCreatedChips"].append(os.path.splitext(chip.replace("69F3A590_",""))[0])
        f.seek(0)
        json.dump(settings, f, indent=4)
        f.truncate()
    return True


def available_projects():
    projects = [f for f in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, f))]
    return projects

def available_chips():
    chips = {}
    with urllib.request.urlopen("https://raw.githubusercontent.com/y2k04/dlscc/repo/repo.json") as url:
        data = json.loads(url.read().decode())
        chips = data["index"]["69F3A590"]
        print(chips)
        return chips

            
@app.route("/")
def home():
    """Display the home page"""
    projects = available_projects()
    chips = available_chips()
    return render_template("home.html", projects=projects, chips=chips)

@app.route("/download", methods=["POST"])
def download():
    chip = request.args.get("chip")
    project = request.args.get("pro")
    downlaodChip(chip, project)
    return jsonify(status=200, warnings=DE, hStatus="Chip downloaded succesfully")
    

while True:
    app.run()