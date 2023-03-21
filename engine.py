import os
import sys
import subprocess
from functools import partial
import json
import re
from collections import defaultdict
import openai
import requests
import random
import shutil
import time


from prompts.prompts import prompt
BASE_MODEL = "gpt-4" # gpt-3.5-turbo
OPENAI_KEY = "sk-xxxxxx"
SPELLBOOK_APP_URL = "https://dashboard.scale.com/spellbook/api/v2/deploy/vy53d52"
SPELLBOOK_API_KEY = "xxxxxx"
LIVESTREAM = True

APP_TEMPLATES = {
    "nextjs_todo_app": {
        "goal": 'Identify every step needed to create a basic Todo App called "doto" using Next.js. Initialize the app using the create-next-app library.',
        "constraints": """
# - This app will not have a database. 
# - This app will not have the ability to do user authentication.
# - This app will be a stand-alone web application
# - This app will be deployed to Vercel
# - This app should not need to be configured to run (for example, no environment variables)
# - This app should not use any 3rd party APIs (OAuth, Stripe, Databases, etc.)
        """.strip(),
        "feature_request": "What is a feature that would make this application more useful, beautiful, interesting, or engaging to its users?"
    },

    "html_todo_app": {
        "goal": "Identify every step needed to create a basic HTML Todo App using JQuery and a modern UX framework like Materialize.",
        "constraints": """
# - This app will not have a database. 
# - This app will not have the ability to do user authentication.
# - This app will be a stand-alone web application
# - This app should not need to be configured to run (for example, no environment variables)
# - This app should not use any 3rd party APIs (OAuth, Stripe, Databases, etc.)
        """.strip(),
        "feature_request": "What is a feature that would make this application more useful, beautiful, interesting, or engaging to its users?"
    },

    "python_function": {
        "goal": "Create a file, `coolness.py`, that has a basic Python function. The function takes in a list of numbers, does something cool, returns the sum of the numbers.",
        "constraints": """
This 'app' should remain in one file 
Never, ever delete any code that you write
""".strip(),
        "feature_request": "What is a feature that would make this application more useful, interesting, or engaging to its users? "
    }
}

APP_TO_BUILD = "html_todo_app" # Which template above do you want to try and build
N_STEPS = 2 # How many steps do you want to let this run for?

openai.api_key = OPENAI_KEY

# Good but optional things to do:
# npm install --global prettier - get better formatting when we write files

# Given a path, list all the files in the path recusively and return a list of files
def list_files(path):
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_list.append(os.path.join(root, file))

    # Remove any files in the .git folder and the .next folder and the node_modules folder
    file_list = [file for file in file_list if '.git' not in file and '.next' not in file and 'node_modules' not in file]

    # Ignore any package-lock.json files
    file_list = [file for file in file_list if 'package-lock.json' not in file]

    # Filter out any files in the global .gitignore 
    with open('.gitignore', 'r') as f:
        ignore_list = f.read().splitlines()
        # Ensure that files in ignored folders are also filtered out
        ignore_list = [os.path.join(path, file) for file in ignore_list]
        file_list = [file for file in file_list if file not in ignore_list]
    
    return file_list

# Given a list of files, return a formatted "pretty print" list of files such that files in folders are indented
def pretty_print_files(file_list, start_directory):
    tree = defaultdict(list)

    def build_tree(file_path, node):
        if not file_path:
            return
        part, *rest = file_path
        if part not in node:
            node[part] = defaultdict(list)
        build_tree(rest, node[part])

    for path in file_list:
        parts = path.split(os.path.sep)
        # Find the index of the start directory
        try:
            start_directory_index = parts.index(start_directory) + 1
            build_tree(parts[start_directory_index:], tree)
        except ValueError:
            raise f"Error: '{start_directory}' not found in the path '{path}'"
 

    def print_node(node, indent=0):
        output = []
        for key, value in node.items():
            output.append("  " * indent + key)
            if value:
                output.extend(print_node(value, indent + 1))
        return output

    return "\n".join(print_node(tree))

# Given a command, run the command and return the output + pwd
def run_command(active_dir, command, live_stream=False):
    # TODO: Consider exporting .env variables to the command
    # TODO: Kill polling commands after a certain amount of time, i.e. npm run dev
    
    # Change the directory to the active directory
    # Return the pwd after the command runs 
    command = f'cd {active_dir} && {command} && echo "|PWD|$(pwd)"'

    # my_env = os.environ.copy()
    # my_env["PYTHONUNBUFFERED"] = "1"

    # Run the command and get the output
    p = subprocess.Popen(
        [command], 
        shell=True, 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        bufsize=1, 
        universal_newlines=True,
        # env=my_env
    )

    input_str = "\n"

    output = ""

    # Get the output and error char by char, and livestream the output
    for char in iter(partial(p.stdout.readline, 1), ''):
        if live_stream and char:
            sys.stdout.write(char)  # livestream the output
        output += char
        # TODO : Handle better if 'Press any key to continue...' type stuff in line - for now, press enter after each line
        try:
            p.stdin.write(input_str)
            p.stdin.flush()
        except:
            pass
        
    # TODO: Maybe more gracefully handle this - seems to close the stdin too early, resulting in BrokenPipeError: [Errno 32] Broken pipe
    # Close the stdin after sending input
    try:
        p.stdin.close()
    except:
        pass

    # Wait for the process to finish
    return_code = p.wait()

    # TODO: Handle errors?
    error = p.stderr.read()
    p.stderr.close()
    
    # Remove the last newline character
    output = (output + error).strip()

    return {
        'command': command,
        'output': output.split('|PWD|')[0],
        'pwd': output.split('|PWD|')[-1].split("\n")[0] if '|PWD|' in output else active_dir,
        'had_error': return_code != 0
    }

# Given a file name and content, create the file and write the content
def create_file(active_dir, file_name, content):
    file_path = active_dir + os.sep + file_name
    # If the folder does not exist, create it
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    # TODO: Handle .env files by copying parent .env file if one exists

    # Create the file and write the content
    with open(file_path, 'w') as f:
        f.write(content)

    try:
        run_command(active_dir, f'prettier --write {file_path}')
    except:
        pass

# Given a file name, delete the file
def delete_file(active_dir, file_name):
    file_path = active_dir + os.sep + file_name
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass

# Given a file path, return the file contents - optionally, specify the active directory to do local search
def get_file_contents(file_name, active_dir=None):
    file_path = file_name if active_dir is None else active_dir + os.sep + file_name
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read()
    else:
        return None

# Given an old file name and a new file name, rename the file
def rename_file(active_dir, old_file_name, new_file_name):
    old_file_path = active_dir + os.sep + old_file_name
    new_file_path = active_dir + os.sep + new_file_name

    if os.path.exists(old_file_path):
        os.rename(old_file_path, new_file_path)

# Return .env keys
def get_env_key_names():
    env_keys = []
    with open('.env', 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            if '=' in line:
                env_keys.append(line.split('=')[0])
    return env_keys

def take_action(active_dir, action, replay=None):
    if 'actionType' not in action:
        if (replay is not None):
            replay.add_debug(f"Tried to process action:\n{action}\n...but it did not have an actionType")
        return None
    
    if action['actionType'] == 'runTerminal':
        # Validate that the content field exists
        if 'content' not in action:
            if (replay is not None):
                replay.add_debug(f"Tried to run terminal command:\n{action['content'] if 'content' in action else '<Invalid Command>'}\n...but it did not have 'real' content")
            return None
        print("Running command: " + action['content'])
        cmdResult = run_command(active_dir, action['content'], LIVESTREAM)

        # TODO: Handle errors by asking GPT-4 to fix the error
        if cmdResult['had_error']:
            if (replay is not None):
                replay.add_debug(f"Command '{action['content']}' had an error\n{cmdResult['output']}\nSkipping this action")
            # raise Exception(f"Error: Command '{action['content']}' had an error")
        
        print("Successfully ran command: " + action['content'] + " | Working Directory: " + active_dir)
        
        return cmdResult
            
    elif action['actionType'] == 'createFile':
        # Validate that the content field exists and has length > 5 characters
        if 'content' not in action or 'path' not in action or len(action['content']) < 5:
            if (replay is not None):
                replay.add_debug(f"Tried to create file:\n{action['path'] if 'path' in action else '<Invalid Path>'}\n...but it did not have 'real' content")
            return None
        create_file(active_dir, action['path'], action['content'])
        print("Successfully created file: " + action['path'])

        return None

    # TODO: See if we can do partial updates to files, right now, edit = overwrite
    elif action['actionType'] == 'editFile':
        if 'content' not in action or 'path' not in action or len(action['content']) < 5:
            if (replay is not None):
                replay.add_debug(f"Tried to edit file:\n{action['path'] if 'path' in action else '<Invalid Path>'}\n...but it did not have 'real' content")
            return None
        create_file(active_dir, action['path'], action['content'])
        print("Successfully created file: " + action['path'])

        return None
    
    elif action['actionType'] == 'renameFile':
        if 'content' not in action or 'path' not in action or len(action['content']) < 5:
            if (replay is not None):
                replay.add_debug(f"Tried to rename file:\n{action['path'] if 'path' in action else '<Invalid Path>'}\n...but it did not have a 'real' new path > 5 characters")
            return None
        rename_file(active_dir, action['path'], action['content'])
        print("Successfully renamed file: " + action['path'] + " to " + action['content'])

        return None

    elif action['actionType'] == 'deleteFile':
        if 'path' not in action:
            if (replay is not None):
                replay.add_debug(f"Tried to delete file ...but it did not have a path")
            return None
        delete_file(active_dir, action['path'])
        print("Successfully deleted file: " + action['path'])

        return None
    
    else:
        if (replay is not None):
            replay.add_debug(f"Tried to process action:\n{action}\n...but it had an invalid action type")
        # raise f"Error: Invalid action type '{action['actionType']}'"

def sanitize_action(action):
    # Determine if the action is blocking (i.e. npm run dev) or non-blocking (i.e. createFile, npm install)

    # Validate the JSON schema

    # Add is_valid field to action?

    return action

# Ask ChatGPT for a response to a message, or a list of messages        
def chatgpt(message = "", messages = [], num_responses=1, max_tokens=2000, temperature=1, top_p=1, model="gpt-3.5-turbo"):
    # If both message and messages are set, throw an error
    if message and len(messages):
        raise Exception("Error: Both message and messages are set. Please only set one of the two.")
    # If neither message or messages are set, throw an error
    if not message and not len(messages):
        raise Exception("Error: Neither message or messages are set. Please set one of the two.")
    
    combined_messages = messages.copy()
    # If message is set, add it to the messages array
    if message:
        combined_messages.append({"role": "user", "content": message})
    
    print("Asking ChatGPT for a response...")
    response = openai.ChatCompletion.create(
        model=model,
        n=num_responses,
        messages=combined_messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    print("Successfully got response from ChatGPT")
    return {
        'text': response["choices"][0]["message"]["content"],
        'raw': response
    }

# GPT4 via Spellbook
def spellbook(message = ""):
    response = requests.post(
        SPELLBOOK_APP_URL, 
        json={
            "input": {
                "input": message
            }
        },
        headers={
            "Authorization": f"Basic {SPELLBOOK_API_KEY}",
            "Content-Type": "application/json"
        }
    )
    return {
        'text': response.json()["output"],
        'raw': response
    }

# Given a string with JSON objects included, extract and load them into a list
def extract_json_from_text(text):
    json_objects = []
    for match in re.finditer(r'\{[\s\S]*?\}', text):
        try:
            json_object = json.loads(match.group())
            json_objects.append(json_object)
        except json.JSONDecodeError:
            pass
    return json_objects

def extract_json_from_text2(text, nCorrections = 1):
    # This function does two kind of cool things:
    # 1. It extracts only top-level JSON blobs from a string 
    # 2. It attempts to fix JSON blobs that are not valid JSON with GPT with redo counter
    json_like_blobs = []
    json_blobs = []
    depth = 0
    start = None
    for i, c in enumerate(text):
        if c == "{":
            if depth == 0:
                start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start is not None:
                json_like_blobs.append(text[start:i+1])
                start = None
    
    for blob in json_like_blobs:
        try:
            json_object = json.loads(blob)
            json_blobs.append(json_object)
        except json.JSONDecodeError:
            if nCorrections == 0:
                print("Error: Could not fix JSON blob: " + blob)
                pass

            print("Invalid JSON recieved, trying to fix...")

            json_correction_prompt = prompt("jsonCorrection", { '|JSON_BLOB|': blob })
            json_correction = chatgpt(message=json_correction_prompt["prompt"], model="gpt-3.5-turbo")
            extracted_json = extract_json_from_text2(json_correction["text"], nCorrections - 1)
            if len(extracted_json) == 1:
                json_blobs.append(extracted_json[0])

    return json_blobs

# Make a "Replay" class that will hold all the information about the session
class Replay:
    def __init__(self, name, use_debug_mode=False, should_save_html=True, should_save_json=True):
        self.name = name
        self.use_debug_mode = use_debug_mode
        self.should_save_html = should_save_html
        self.should_save_json = should_save_json
        self.messages = []
        self.prompts = []
        self.actions = []
        self.debug = []
        self.timeline = []

    # Function to sanitize HTML strings to be displayed in the browser
    def sanitize_html(self, html):
        return html.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

    def to_json(self):
        return {
            "messages": self.messages,
            "prompts": self.prompts,
            "actions": self.actions,
            "debug": self.debug,
            "timeline": self.timeline
        }
    
    def add_prompt(self, prompt):
        self.prompts.append(prompt)
        self.timeline.append({
            "type": "prompt",
            "prompt": prompt
        })
        if (self.use_debug_mode):
            print(f"[{self.name}] Prompt:\n" + prompt)
        if (self.should_save_html):
            self.save_html()
        if (self.should_save_json):
            self.save_json()

    def add_action(self, action):
        self.actions.append(action)
        self.timeline.append({
            "type": "action",
            "action": action
        })
        if (self.use_debug_mode):
            print(f"[{self.name}] Action:\n" + str(action["content"]) if "content" in action else "")
        if (self.should_save_html):
            self.save_html()
        if (self.should_save_json):
            self.save_json()


    def add_message(self, message):
        self.messages.append(message)
        self.timeline.append({
            "type": "message",
            "message": message
        })
        if (self.use_debug_mode):
            print(f"[{self.name}] Message:\n" + message)
        if (self.should_save_html):
            self.save_html()
        if (self.should_save_json):
            self.save_json()

    def add_debug(self, debug):
        self.debug.append(debug)
        self.timeline.append({
            "type": "debug",
            "debug": debug
        })
        if (self.use_debug_mode):
            print(f"[{self.name}] Debug:\n" + debug)  
        if (self.should_save_html):
            self.save_html()
        if (self.should_save_json):
            self.save_json()         

    def save_json(self):
        with open("replays" + os.sep + self.name + ".json", "w") as f:
            json.dump(self.to_json(), f, indent=2)

    def save_html(self):
        # Generate a HTML file with the replay
        with open("replays" + os.sep + self.name + ".html", "w") as f:
            # Write the start of a basic HTML file
            f.write(f"""<!DOCTYPE html>
<html>
    <head>
        <title>Replay {self.name}</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Source Code Pro', monospace;
            }}

            h3: {{ margin: 0; }}

            .event {{
                margin: 10px;
                padding: 10px;
                border: 1px solid black;
            }} 

            .typeprompt {{
                background-color: #ffcccc;
            }}

            .typeaction {{
                background-color: #ccffcc;
            }}

            .typemessage {{
                background-color: #ccccff;
            }}

            .typedebug {{
                background-color: #cccccc;
            }}

        </style>
    </head>
    <body>
        <h1>Replay {self.name}</h1>
            """)

            for event in self.timeline:
                f.write(f"<div class='event type{event['type']}'>")
                
                if event["type"] == "prompt":
                    f.write(f"<h3>Prompt:</h3>{self.sanitize_html(event['prompt'])}")

                elif event["type"] == "action":
                    f.write(f"""
                        <h3>Action:</h3>      
                        {f"<b>Type:</b> {self.sanitize_html(event['action']['actionType'])}<br>" if 'actionType' in event['action'] else ""}
                        {f"<b>Path:</b> {self.sanitize_html(event['action']['path'])}<br>" if 'path' in event['action'] else ""}
                        {f"<b>Content:</b><br> {self.sanitize_html(event['action']['content'])}<br>" if 'content' in event['action'] else ""}
                    """)

                elif event["type"] == "message":
                    f.write(f"<h3>Response:</h3>{self.sanitize_html(event['message'])}")

                elif event["type"] == "debug":
                    f.write(f"<h3>Debug:</h3>{self.sanitize_html(event['debug'])}")

                f.write(f"</div>")

            # Write the end of the HTML file
            f.write("""
    </body>
</html>
            """)



# =================================================================================================
# =====================================  START PROGRAM  ===========================================
# =================================================================================================

# Make an epoch time string
epoch_time = str(int(time.time()))
active_dir = os.getcwd() + os.sep + f"projects/project_{epoch_time}" # Set and track active directory to default to pwd + projects folder
# Make a new directory for the project
os.mkdir(active_dir)
print(f"Kicking off 'project_{epoch_time}', fingers crossed!")
print("=======================================================")

# Copy the .gitignore and .env files to the new project directory
shutil.copyfile('.gitignore', active_dir + os.sep + '.gitignore')
shutil.copyfile('.env', active_dir + os.sep + '.env')

file_map = {} # TODO: Stores file paths, token lengths, and descriptions of file contents
features = [] # Maintains a list of features added
replay = Replay(str(epoch_time), use_debug_mode=True)

# Build Base
replay.add_debug("Asking for the base action steps...")
# Generate the prompt to ask for the base
base_prompt = prompt("basePrompt", { '|BASE_GOAL|': APP_TEMPLATES[APP_TO_BUILD]['goal'] })["prompt"] + "\n\n" + prompt("actionObject")["prompt"] + "\n\nWhen setting the `content` field to code, write the entire code needed.\n\n### Step 1: "
replay.add_prompt(base_prompt)
# Get the base action steps from GPT-4
base_res = chatgpt(message=base_prompt)['text']
replay.add_message(base_res)
# Extract the JSON from the text
action_sequence = extract_json_from_text2(base_res)

# Execute the base action steps
for action in action_sequence:
    replay.add_action(action)
    outcome = take_action(active_dir, action)
    if 'actionType' in action and action['actionType'] == 'runTerminal':
        active_dir = outcome['pwd']

# =======================================================================================
# === Evaluate the base we just made, does it actually work? does it do what we want? ===
# =======================================================================================

base_goal_met = False
while not base_goal_met:
    print("")
    replay.add_debug("Asking for the base evaluation...")
    
    # Get Prompt Vars ready
    dir_mapping_str = pretty_print_files(list_files(active_dir), active_dir.split(os.path.sep)[-1])
    file_context = ""
    file_map = list_files(active_dir)
    for file_path in file_map:
        if get_file_contents(file_path) == None:
            continue
        file_context += f"\n\n### {file_path}\n{get_file_contents(file_path)}" 
    
    base_evaluation = prompt("baseEvaluation", { 
        '|BASE_GOAL|':  APP_TEMPLATES[APP_TO_BUILD]['goal'],
        '|DIR_TREE|': dir_mapping_str,
        '|FILE_CONTEXT|': file_context,
    }
    )["prompt"]
    replay.add_prompt(base_evaluation)

    # Get the base evaluation from GPT-4
    base_evaluation_res = chatgpt(message=base_evaluation)['text']
    replay.add_message(base_evaluation_res)
    
    # Identify if any steps were returned to fix the base
    action_sequence = extract_json_from_text2(base_evaluation_res)
    # If no steps and the response contains "Goal Met", then we're good
    if len(action_sequence) == 0 and "Goal Met" in base_evaluation_res:       
        base_goal_met = True
        replay.add_debug("Base goal met! Now for the fun stuff...")
    else:
        # If the base goal is not met, take the steps to fix it
        replay.add_debug("Taking actions to fix the base...")
        for step in action_sequence:
            take_action(active_dir, step)
            replay.add_action(step)

# ========================================================
# === Let's have some fun and make this app delightful ===
# ========================================================

NUM_STEPS_DONE = 0

while NUM_STEPS_DONE < N_STEPS:
    # Identify a feature that would improve the app based on categories (UX, UI, Functionality, etc.)
    feature_request = prompt("featureRequest", { 
        '|APPLICATION_SUMMARY|':  APP_TEMPLATES[APP_TO_BUILD]['goal'], 
        '|APPLICATION_CONSTRAINTS|':  APP_TEMPLATES[APP_TO_BUILD]['constraints'],
        '|EXISTING_FEATURES|': '\n'.join([f"**{feature['name']}** - {feature['brief_summary']}" for feature in features]),
        '|FEATURE_REQUEST_QUESTION|':  APP_TEMPLATES[APP_TO_BUILD]['feature_request'],
     })
    replay.add_prompt(feature_request['prompt'])
  
    # Ask to generate a feature
    chat_res = chatgpt(message=feature_request['prompt'])['text']
    replay.add_message(chat_res)
    
    feature_response = extract_json_from_text2(feature_request["prefix"] + chat_res + feature_request["suffix"])[0]

    # If the feature is valid (has a `name`, `brief_summary`, and a `how_to`), add it to the list of features
    if 'name' not in feature_response or 'brief_summary' not in feature_response or 'how_to' not in feature_response:
        replay.add_debug("Error: Invalid feature response - skipping for now")
        continue
    
    # If valid feature, let's keep going
    replay.add_debug("About to try adding feature: " + feature_response['name'])
    features.append(feature_response)
    
    # Ask which files to load in memory - Provide folder structure and file names
    dir_mapping_str = pretty_print_files(list_files(active_dir), active_dir.split(os.path.sep)[-1])
    file_mapping_request = prompt("fileMappingRequest", {
        '|DIR_TREE|': dir_mapping_str,
        '|FEATURE_REQUEST|': feature_response['name'],
        '|FEATURE_REQUEST_SUMMARY|': feature_response['brief_summary'],
        '|FEATURE_REQUEST_HOW_TO|': feature_response['how_to'],
    })

    # Ask GPT for file mappings
    replay.add_prompt(file_mapping_request['prompt'])
    file_mappings = chatgpt(message=file_mapping_request["prompt"])
    replay.add_message(file_mapping_request["prefix"] + file_mappings["text"] + file_mapping_request["suffix"])
    
    file_map_res = extract_json_from_text2(file_mapping_request["prefix"] + file_mappings["text"] + file_mapping_request["suffix"])[0]
    if ("fileMapping" not in file_map_res):
        replay.add_debug(f"Error: Invalid file mapping response\n\n{file_mappings['text']}")
        continue

    # Parse file mappings into a list of file paths
    file_map = file_map_res["fileMapping"]
    
    # Generate File Context of each file
    file_context = ""
    # TODO: If just file name or partial path, then we need to find the full path - this is a hacky way to do it
    for file_path in file_map:
        for file in list_files(active_dir):
            if file_path in file:
                file_path = file
        if get_file_contents(file_path) == None:
            continue
        file_context += f"\n\n### {file_path}\n{get_file_contents(file_path)}" 
    
    # Convert feature into Action Objects w/ Context
    feature_actions_prompt = prompt("stepsToTake", {
        '|DIR_TREE|': dir_mapping_str,
        '|FEATURE_REQUEST|': feature_response['name'],
        '|FEATURE_REQUEST_SUMMARY|': feature_response['brief_summary'],
        '|FEATURE_REQUEST_HOW_TO|': feature_response['how_to'],
        '|FILE_CONTEXT|': file_context,
        '|DIR_TREE|': dir_mapping_str,
        '|APPLICATION_CONSTRAINTS|':  APP_TEMPLATES[APP_TO_BUILD]['constraints'],
    })
    replay.add_prompt(feature_actions_prompt['prompt'])
    feature_actions = chatgpt(message=feature_actions_prompt["prompt"])
    replay.add_message(feature_actions_prompt["prefix"] + feature_actions["text"] + feature_actions_prompt["suffix"])
    feature_actions = extract_json_from_text2(feature_actions_prompt["prefix"] + feature_actions["text"] + feature_actions_prompt["suffix"])
    
    # Actually try and do the feature!
    for action in feature_actions:
        replay.add_action(action)
        outcome = take_action(active_dir, action)
        if 'actionType' in action and action['actionType'] == 'runTerminal':
            active_dir = outcome['pwd']

    # Increment the number of steps done
    NUM_STEPS_DONE += 1

# # Load in Action Sequence for Testing

# # with open('action_sequences/todo1.json', 'r') as f:
# #     action_sequence = json.load(f)
#     # for action in action_sequence:
#     #     outcome = take_action(active_dir, action)
#     #     if action['actionType'] == 'runTerminal':
#     #         active_dir = outcome['pwd']

# # print(pretty_print_files(list_files(active_dir), active_dir.split(os.path.sep)[-1]))