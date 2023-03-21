import re

# TODO: Figure out a graceful way to share common text between prompts, or just make top-level vars...

# Get all text files in the current working directory
def prompt(prompt, token_replacement_dict=None):
    prompts = {
        "basePrompt": {
            "prompt": """
|BASE_GOAL| 
For each step to do, create an Action Object to describe what needs to be done.

Create a step for every action that needs to be taken to accomplish the goal, including installation, running commands, and editing files.

You should always make up names given context instead of using placeholder values like <project name>.
        """,
            "prefix":"",
            "suffix":""
        }, 

        "baseEvaluation": {
            "prompt": """
The goal of this task was to |BASE_GOAL|

Please review the files in the repository and confirm that the goal was met. If the goal was met, simply respond with "Goal Met".
If the goal was not met, create a step for every action that needs to be taken to accomplish the goal. Include installation, running commands, and editing files.

Write each step as an Action Object.

An Action Object JSON can be defined with the following properties:

### actionType: enum
A required field representing the type of action to perform. It must be one of the following values:

- runTerminal: Execute a command in a terminal or command prompt window.
- createFile: Create a new file with the specified contents.
- editFile: Modify an existing file by replacing all of its content with something new.
- renameFile: Rename an existing file.
- deleteFile: Delete an existing file.

### path: string
A required field specifying the location of the file to create, edit, rename, or delete. The path should include the file's name and extension. For example: `src/components/Header.js`. This field is not needed for the `runTerminal` actionType.

### content: string
A required field containing the primary information related to the action. Depending on the actionType, this could be:

- Code to execute in a terminal window for `runTerminal`.
- Contents of a file to create for `createFile`.
- New code to replace all of the current code in an existing file for `editFile`
- The new name of the file to be renamed for `renameFile`
The `content` field can be blank for the `deleteFile` action type.

The directory structure is as follows:
|DIR_TREE|

## Key Files
|FILE_CONTEXT|

--

        """,
            "prefix":"",
            "suffix":""
        }, 

        "featureImplementation": {
            "prompt": """
The goal of this task is to implement the following feature:


Please review the files in the repository and confirm that the goal was met. If the goal was met, simply respond with "Goal Met".
If the goal was not met, create a step for every action that needs to be taken to accomplish the goal. Include installation, running commands, and editing files.

Write each step as an Action Object.

An Action Object JSON can be defined with the following properties:

### actionType: enum
A required field representing the type of action to perform. It must be one of the following values:

- runTerminal: Execute a command in a terminal or command prompt window.
- createFile: Create a new file with the specified contents.
- editFile: Modify an existing file by replacing all of its content with something new.
- renameFile: Rename an existing file.
- deleteFile: Delete an existing file.

### path: string
A required field specifying the location of the file to create, edit, rename, or delete. The path should include the file's name and extension. For example: `src/components/Header.js`. This field is not needed for the `runTerminal` actionType.

### content: string
A required field containing the primary information related to the action. Depending on the actionType, this could be:

- Code to execute in a terminal window for `runTerminal`.
- Contents of a file to create for `createFile`, always written in full.
- New code to replace all of the current code in an existing file for `editFile`, always written in full.
- The new name of the file to be renamed for `renameFile`
The `content` field can be blank for the `deleteFile` action type.

The directory structure is as follows:
|DIR_TREE|

## Key Files
|FILE_CONTEXT|

--

        """,
            "prefix":"",
            "suffix":""
        }, 

        "actionObject": {
            "prompt": """
An Action Object JSON can be defined with the following properties:

### actionType: enum
A required field representing the type of action to perform. It must be one of the following values:

- runTerminal: Execute a command in a terminal or command prompt window.
- createFile: Create a new file with the specified contents.
- editFile: Modify an existing file by replacing all of its content with something new.
- renameFile: Rename an existing file.
- deleteFile: Delete an existing file.

### path: string
A required field specifying the location of the file to create, edit, rename, or delete. The path should include the file's name and extension. For example: `src/components/Header.js`. This field is not needed for the `runTerminal` actionType.

### content: string
A required field containing the primary information related to the action. Depending on the actionType, this could be:

- Code to execute in a terminal window for `runTerminal`.
- Contents of a file to create for `createFile`, always written in full.
- New code to replace all of the current code in an existing file for `editFile`, always written in full.
- The new name of the file to be renamed for `renameFile`
The `content` field can be blank for the `deleteFile` action type.
            """, 
            "prefix": "",
            "suffix": ""
        }, 

        "runCommandErrorHandling": {
            "prompt": """
    I received this error when running
    ```
    |COMMAND|
    ```

    Error:
    ```
    |ERROR|
    ```

    You are a language model, sometimes you will make up packages or words that don't actually exist. That's OK, but I need to write safer, more robust code.

    Can you suggest a new command to run that would avoid any issues related to you making up things like package names or flags? 
            """,
            "prefix": "",
            "suffix": ""
        },

        "featureRequest": {
            "prompt": """
## Application Summary:
|APPLICATION_SUMMARY|

## Application Constraints
|APPLICATION_CONSTRAINTS|

## Existing Features:
|EXISTING_FEATURES|

## Question:
|FEATURE_REQUEST_QUESTION|

The feature should not violate the application constraints.

Please provide a JSON blob describing the feature with the following values:
 - `name` - Name of Feature
 - `brief_summary` - A one-sentence long brief summary of the feature
 - `how_to` - A description of how this feature could work

 {
            """,
            "prefix": " {",
            "suffix": " "
         },

        "fileMappingRequest": { 
            "prompt": """
You will be implementing the following feature request:
**|FEATURE_REQUEST|** - |FEATURE_REQUEST_SUMMARY|

|FEATURE_REQUEST_HOW_TO|

The files in this application are organized in a specific way. The file structure is as follows:
|DIR_TREE|

Return a JSON blob with the following properties:
- `fileMapping` - An array of file paths to existing files that will need to be edited. The file paths should be relative to the root of the project. For example, if you want to create a file at `src/components/Header.js`, an element in the array would be `src/components/Header.js`.

{
""",
            "prefix": " {",
            "suffix": " "
        },

        "stepsToTake": { 
            "prompt": """
## Feature Request
You will be implementing the following feature request:
**|FEATURE_REQUEST|** - |FEATURE_REQUEST_SUMMARY|

|FEATURE_REQUEST_HOW_TO|

Please remember the following application constraints:
|APPLICATION_CONSTRAINTS|

## Source Directory
The files in this application are organized in a specific way. The file structure is as follows:
|DIR_TREE|

## File Context
For context, some files have been added below:
|FILE_CONTEXT|

## Steps to Build Feature
You will accomplish this feature request in steps. 

Write each step as an Action Object, where each object describes the step that will be needed to accomplish this.

An Action Object JSON can be defined with the following properties:

### actionType: enum
A required field representing the type of action to perform. It must be one of the following values:

- runTerminal: Execute a command in a terminal or command prompt window.
- createFile: Create a new file with the specified contents.
- editFile: Modify an existing file by replacing all of its content with something new.
- renameFile: Rename an existing file.
- deleteFile: Delete an existing file.

### path: string
A required field specifying the location of the file to create, edit, rename, or delete. The path should include the file's name and extension. For example: `src/components/Header.js`. This field is not needed for the `runTerminal` actionType.

### content: string
A required field containing the primary information related to the action. Depending on the actionType, this could be:

- Code to execute in a terminal window for `runTerminal`.
- Contents of a file to create for `createFile`, always written in full.
- New code to replace all of the current code in an existing file for `editFile`, always written in full.
- The new name of the file to be renamed for `renameFile`
The `content` field can be blank for the `deleteFile` action type.

### Step 1: 
{ 
    "actionType": \""
""",
            "prefix": " {\"actionType\": \"",
            "suffix": " "
        },

        "jsonCorrection": {
            "prompt": """
Please correct any formatting or completion errors in following JSON blob, returning only the valid JSON blob.
|JSON_BLOB|
""",
            "prefix": "",
            "suffix": ""
        }
    }

    # Ensure prompt is in the keys of prompts
    if prompt not in prompts:
        raise Exception(f"Error: Prompt '{prompt}' is not in the prompt template dictionary.")

    # If any token replacements are needed, do them here
    if token_replacement_dict:
        for placeholder, value in token_replacement_dict.items():
            for promptKey, promptOjbj in prompts.items():
                prompts[promptKey]["prompt"] = promptOjbj["prompt"].replace(placeholder, value.strip())

    # See if any tokens are left in the prompt
    tokens = re.findall(r'\|(.+?)\|', prompts[prompt]["prompt"])

    # If there are tokens left, raise an error
    if tokens:
        raise Exception(f"Error: Prompt '{prompt}' still has tokens left unreplaced: {tokens}")
    
    # Strip whitepace from the prompt
    prompts[prompt]["prompt"] = prompts[prompt]["prompt"].strip()

    # Return the prompt
    return prompts[prompt]