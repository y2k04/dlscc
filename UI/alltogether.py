import os
import json
import urllib.request
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Define constants
USER_DIR = os.path.expanduser("~")
GITHUB_REPO_URL = "https://api.github.com/repos/y2k04/dlscc/contents"
PROJECTS_DIR = os.path.join(USER_DIR, "AppData", "LocalLow", "SebastianLague", "Digital Logic Sim", "V1", "Projects")
CHIP_FILE_EXT = ".json"
DE = []

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Chip Downloader</title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
</head>
<body>
    <h1>Chip Downloader</h1>
    <form>
        <label for="project">Select a project:</label>
        <select id="project" name="project">
            {% for project in projects %}
                <option value="{{ project }}">{{ project }}</option>
            {% endfor %}
        </select>
        <br>
        <br>
        <label for="chip">Select a chip:</label>
        <select id="chip">
            {% for chip in chips %}
                <option value="{{ chip }}">{{ chip }}</option>
            {% endfor %}
        </select>

        <br>
        <br>
        <button type="button" class="button-17" onclick="downloadChip()">Download Chip</button>
    </form>
    <div id="warnings"></div>
    <div id="status"></div>

    <style>
  select {
    font-size: 16px;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #fff;
    color: #333;
    box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1);
  }
  .button-17 {
  align-items: center;
  appearance: none;
  background-color: #fff;
  border-radius: 24px;
  border-style: none;
  box-shadow: rgba(0, 0, 0, .2) 0 3px 5px -1px,rgba(0, 0, 0, .14) 0 6px 10px 0,rgba(0, 0, 0, .12) 0 1px 18px 0;
  box-sizing: border-box;
  color: #3c4043;
  cursor: pointer;
  display: inline-flex;
  fill: currentcolor;
  font-family: "Google Sans",Roboto,Arial,sans-serif;
  font-size: 14px;
  font-weight: 500;
  height: 48px;
  justify-content: center;
  letter-spacing: .25px;
  line-height: normal;
  max-width: 100%;
  overflow: visible;
  padding: 2px 24px;
  position: relative;
  text-align: center;
  text-transform: none;
  transition: box-shadow 280ms cubic-bezier(.4, 0, .2, 1),opacity 15ms linear 30ms,transform 270ms cubic-bezier(0, 0, .2, 1) 0ms;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  width: auto;
  will-change: transform,opacity;
  z-index: 0;
}

.button-17:hover {
  background: #F6F9FE;
  color: #174ea6;
}

.button-17:active {
  box-shadow: 0 4px 4px 0 rgb(60 64 67 / 30%), 0 8px 12px 6px rgb(60 64 67 / 15%);
  outline: none;
}

.button-17:focus {
  outline: none;
  border: 2px solid #4285f4;
}

.button-17:not(:disabled) {
  box-shadow: rgba(60, 64, 67, .3) 0 1px 3px 0, rgba(60, 64, 67, .15) 0 4px 8px 3px;
}

.button-17:not(:disabled):hover {
  box-shadow: rgba(60, 64, 67, .3) 0 2px 3px 0, rgba(60, 64, 67, .15) 0 6px 10px 4px;
}

.button-17:not(:disabled):focus {
  box-shadow: rgba(60, 64, 67, .3) 0 1px 3px 0, rgba(60, 64, 67, .15) 0 4px 8px 3px;
}

.button-17:not(:disabled):active {
  box-shadow: rgba(60, 64, 67, .3) 0 4px 4px 0, rgba(60, 64, 67, .15) 0 8px 12px 6px;
}

.button-17:disabled {
  box-shadow: rgba(60, 64, 67, .3) 0 1px 3px 0, rgba(60, 64, 67, .15) 0 4px 8px 3px;
}
</style>

    <script>
        function downloadChip() {
            var chip = document.getElementById("chip").value;
            var pro = document.getElementById("project").value;
            document.getElementById("warnings").innerHTML = "";
            $.post("/download?chip="+chip+"&pro="+pro, function(data, status){
                document.getElementById("warnings").innerHTML = data.warnings;
                document.getElementById("status").innerHTML = data.hStatus;
            });
        }
    </script>
</body>
</html>
"""

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
    return render_template_string(HTML, projects=projects, chips=chips)

@app.route("/download", methods=["POST"])
def download():
    chip = request.args.get("chip")
    project = request.args.get("pro")
    downlaodChip(chip, project)
    return jsonify(status=200, warnings=DE, hStatus="Chip downloaded succesfully")
    

while True:
    app.run()