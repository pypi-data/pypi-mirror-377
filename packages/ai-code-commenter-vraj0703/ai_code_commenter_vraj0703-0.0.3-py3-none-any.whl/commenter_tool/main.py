import sys
import os
import subprocess
import time
import re
import importlib.resources
from pathlib import Path
import textwrap # Import the textwrap module
import argparse # For handling command-line arguments and subcommands
import json


# --- Main Script Logic ---
# Function to enforce the 80-character line limit
def rewrap_comment_block(comment_block: str, width: int = 80) -> str:
    """
    Re-wraps a comment block to a specified width, preserving comment prefixes.

    Args:
        comment_block: The multi-line string representing the comment block.
        width: The maximum line width.

    Returns:
        The reformatted comment block as a single string.
    """
    reformatted_lines = []

    # Heuristic to find the content-bearing lines (ignores lines like /** or */)
    def is_content_line(line):
        return re.search(r'[a-zA-Z0-9]', line)

    for line in comment_block.splitlines():
        if len(line) <= width or not is_content_line(line):
            reformatted_lines.append(line)
            continue

        # Find the indentation and comment prefix (e.g., " * " or "# ")
        match = re.match(r'^(\s*[\*#/]*\s*)', line)
        prefix = match.group(1) if match else ''
        content = line[len(prefix):]

        # Use textwrap to wrap the content of the line
        wrapper = textwrap.TextWrapper(
            width=width,
            initial_indent=prefix,
            subsequent_indent=prefix
        )
        reformatted_lines.extend(wrapper.wrap(content))

    return "\n".join(reformatted_lines)

def generate_comments(file_content, comment_format, comment_syntax, file_path, model_name):
    """
    Calls the Ollama CLI to generate comments for the given code.
    """
    prompt = f"""
    As an experienced software engineer, your task is to analyze the following code 
    and generate a comprehensive comment block that explains it.

    You have three strict rules:
    1. You MUST use the following comment syntax: {comment_syntax}
    2. The content of the comment block MUST strictly follow the format provided below. Replace @ai- with generate comments
    3. Each line in your response MUST NOT exceed 80 characters in length. Wrap all text 
       appropriately to adhere to this rule.

    --- CONTENT FORMAT START ---
    {comment_format}
    --- CONTENT FORMAT END ---

    Here is the code to analyze:
    --- CODE START ---
    {file_content}
    --- CODE END ---

    Generate ONLY the comment block, following all rules. Do not include 
    any other text, explanations, or the original code in your response.
    """

    try:
        command = ['ollama', 'run', model_name, prompt]
        print(f"   ▶️  Executing Ollama for {os.path.basename(file_path)}...")
        start_time = time.time()

        result = subprocess.run(
            command, capture_output=True, text=True, check=True,
            timeout=300, encoding='utf-8'
        )

        duration = time.time() - start_time
        print(f"   ✅ Ollama generation finished in {duration:.2f} seconds.")

        # MODIFIED: Use .rstrip() to preserve leading whitespace from the AI
        # while still cleaning the end of the output.
        return result.stdout.rstrip()

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"   ❌ Error: Ollama command timed out after {duration:.0f} seconds.")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return None


def process_file(file_path, comment_format, comment_syntax, model_name):
    """
    Reads a file, generates comments, and prepends them.
    """
    print(f"\n📄 Processing file: {file_path}")

    try:
        file_size_kb = os.path.getsize(file_path) / 1024
        print(f"   - File size: {file_size_kb:.2f} KB")

        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        if not original_content.strip():
            print("   ⚪ Skipping empty file.")
            return

        new_comments = generate_comments(original_content, comment_format, comment_syntax, file_path, model_name)

        if new_comments:
            # MODIFIED: Enforce 80-char limit programmatically
            print("   - Enforcing 80-character line limit...")
            new_comments = rewrap_comment_block(new_comments, width=80)

            new_content = f"{new_comments}\n\n{original_content}"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"   ✔️ Successfully added comments to {os.path.basename(file_path)}")
        else:
            print(f"   ⚠️ Failed to generate comments for {os.path.basename(file_path)}. Skipping.")

    except Exception as e:
        print(f"   ❌ An unexpected error occurred while processing {file_path}: {e}")

def get_config_path():
    """Returns the path to the user's config directory and ensures it exists."""
    config_dir = Path.home() / ".config" / "commenter"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def load_config():
    """Loads settings from the config.json file."""
    config_file = get_config_path() / "config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return {} # Return empty dict if no config exists yet

def save_config(config_data):
    """Saves settings to the config.json file."""
    config_file = get_config_path() / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    print(f"✅ Configuration saved to {config_file}")

def check_ollama_installed():
    """Checks if the 'ollama' command is available."""
    try:
        subprocess.run(['ollama', '--version'], check=True, capture_output=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def check_and_pull_model(model_name):
    """Checks if a model is downloaded and pulls it if it isn't."""
    print(f"Checking for Ollama model '{model_name}'...")
    try:
        result = subprocess.run(['ollama', 'list'], check=True, capture_output=True, text=True)
        if model_name in result.stdout:
            print(f"Model '{model_name}' is already downloaded.")
            return True
        else:
            print(f"Model '{model_name}' not found. Attempting to download...")
            subprocess.run(['ollama', 'pull', model_name], check=True)
            print(f"✅ Successfully downloaded '{model_name}'.")
            return True
    except Exception as e:
        print(f"❌ Error interacting with Ollama: {e}")
        return False

# --- NEW: Handlers for the 'run' and 'config' commands ---

def handle_run_command(args):
    """Handles the main logic of running the commenter tool."""
    print("--- Starting Commenter ---")
    config = load_config()
    model_name = config.get('model_name', 'llama3') # Default to 'llama3'

    # --- Fallback Logic for Config Files ---
    # Try to use user-defined paths, but fall back to package defaults if they fail.
    try:
        format_path = config.get('format_path')
        if not format_path or not Path(format_path).exists():
            if format_path: print(f"⚠️ Warning: Custom format path not found. Using default.")
            format_ref = importlib.resources.files('commenter_tool') / 'data' / 'format.txt'
            with format_ref.open('r', encoding='utf-8') as f: comment_format = f.read()
        else:
            with open(format_path, 'r', encoding='utf-8') as f: comment_format = f.read()

        syntax_path = config.get('syntax_path')
        if not syntax_path or not Path(syntax_path).exists():
            if syntax_path: print(f"⚠️ Warning: Custom syntax path not found. Using default.")
            syntax_ref = importlib.resources.files('commenter_tool') / 'data' / 'syntax.txt'
            with syntax_ref.open('r', encoding='utf-8') as f: comment_syntax = f.read()
        else:
            with open(syntax_path, 'r', encoding='utf-8') as f: comment_syntax = f.read()
    except Exception as e:
        print(f"❌ Error loading configuration files: {e}")
        return

    # --- Process Files (existing logic) ---
    target_path = args.path
    if os.path.isfile(target_path):
        process_file(target_path, comment_format, comment_syntax, model_name)
    elif os.path.isdir(target_path):
        print(f"📁 Processing all files in directory: {target_path}")
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.go', '.rs', '.java', '.dart')):
                    file_path = os.path.join(root, file)
                    process_file(file_path, comment_format, comment_syntax, model_name)

    print("\n✨ All done!")
# ... folder processing logic ...

def handle_config_command(args):
    """Handles viewing and updating the configuration."""
    print("--- Commenter Configuration ---")
    if not check_ollama_installed():
        print("❌ Ollama is not installed or not in your system's PATH.")
        print("Please install it from https://ollama.com/ and try again.")
        return
    else:
        print("✅ Ollama installation found.")

    config = load_config()

    # Update config if any arguments were passed
    if args.model or args.format_path or args.syntax_path:
        if args.model:
            if check_and_pull_model(args.model):
                config['model_name'] = args.model
        if args.format_path:
            if Path(args.format_path).exists():
                config['format_path'] = args.format_path
                print(f"Set format file path to: {args.format_path}")
            else:
                print(f"⚠️ Warning: Path not found for format file: {args.format_path}")
        if args.syntax_path:
            if Path(args.syntax_path).exists():
                config['syntax_path'] = args.syntax_path
                print(f"Set syntax file path to: {args.syntax_path}")
            else:
                print(f"⚠️ Warning: Path not found for syntax file: {args.syntax_path}")
        save_config(config)
    else:
        # If no arguments, just display the current config
        print("\nCurrent configuration:")
        if not config:
            print("No configuration set. Using defaults.")
        else:
            print(json.dumps(config, indent=2))

def main():
    parser = argparse.ArgumentParser(description="An AI-powered tool to automatically comment code.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # --- Parser for the 'run' command ---
    run_parser = subparsers.add_parser('run', help='Run the commenter on a file or folder.')
    run_parser.add_argument('path', type=str, help='Path to the code file or folder to comment on.')
    run_parser.set_defaults(func=handle_run_command)

    # --- Parser for the 'config' command ---
    config_parser = subparsers.add_parser('config', help='View or set configuration options.')
    config_parser.add_argument('--model', type=str, help='Set the Ollama model name to use (e.g., "llama3", "phi3:mini").')
    config_parser.add_argument('--format-path', type=str, help='Set the absolute path to your custom format.txt file.')
    config_parser.add_argument('--syntax-path', type=str, help='Set the absolute path to your custom syntax.txt file.')
    config_parser.set_defaults(func=handle_config_command)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
