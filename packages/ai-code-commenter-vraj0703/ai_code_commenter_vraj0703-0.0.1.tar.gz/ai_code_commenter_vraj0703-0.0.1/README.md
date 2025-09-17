## AI Code Commenter using Ollama
This Python script automatically generates and prepends comments to your source code files using a locally running Ollama model. It can process a single file or recursively walk through an entire directory, making it easy to document a whole codebase.

The comment style is fully customizable through a simple text file.

## Features
🤖 AI-Powered Commenting: Leverages local LLMs via Ollama to understand code and generate meaningful comments.

📂 Batch Processing: Can run on an entire folder (your codebase) to comment on all supported files recursively.

📄 Single File Mode: Can also target a single file for quick commenting.

🎨 Customizable Format: You define the exact format of the comment block using a format.txt template.

🔌 Simple & Local: No need for external APIs or paid services. It all runs on your machine.

## Prerequisites
Before you begin, ensure you have the following installed and running:

Python 3.6+: The script is written in Python.

Ollama: You must have Ollama installed and the service running on your machine.

An Ollama Model: You need at least one model pulled. For code-related tasks, we recommend llama3 for quality or phi3:mini for speed.

Bash

# Pull a high-quality model (slower, needs ~8GB RAM)
ollama pull llama3

# Or pull a fast, smaller model (needs ~4GB RAM)
ollama pull phi3:mini
## Setup
Download Files: Place the commenter.py script and the format.txt file in the same directory.

Configure the Model (Optional): Open commenter.py and change the OLLAMA_MODEL variable if you want to use a different model than the default (llama3).

Python

# In commenter.py
OLLAMA_MODEL = "phi3:mini" # Example: Changed to a faster model
Customize the Comment Format: Open format.txt and edit it to define your desired comment structure. The script will instruct the AI to follow this format precisely. The default format is:

"""
Author: AI Assistant
Date: <CURRENT_DATE>
Description:
<A high-level summary of the file's purpose in one or two sentences.>

Functions:
- <function_name_1>: <Brief description of what this function does.>
- <function_name_2>: <Brief description of what this function does.>
  """
## How to Run on Your Codebase
You can run the script from your terminal.

To Comment on an Entire Codebase (Folder):
Provide the path to the root folder of your project. The script will automatically find and process all supported code files (e.g., .py, .js, .dart, etc.) inside it and all its subdirectories.

Bash

python commenter.py /path/to/your/project_folder/
Example:

Bash

python commenter.py C:\Users\YourUser\Documents\MyWebApp\
To Comment on a Single File:
Provide the direct path to the specific file you want to comment.

Bash

python commenter.py /path/to/your/file.py
Example:

Bash

python commenter.py C:\Users\YourUser\Documents\MyWebApp\src\utils.py
## Troubleshooting
Timeout Errors
If you see an error like Error: The 'ollama' command timed out..., it means the AI model is taking too long to respond. This usually happens the first time you run it.

Solution 1 (Warm-up): Run a simple command in your terminal before using the script to load the model into memory: ollama run llama3 "Hello!".

Solution 2 (Increase Timeout): Open commenter.py and increase the timeout=300 value to a higher number (e.g., 600 for 10 minutes).

Solution 3 (Use a Smaller Model): A smaller model like phi3:mini is much faster. See the setup section to change the model.