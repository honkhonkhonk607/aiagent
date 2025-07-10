import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python import schema_run_python_file, run_python_file

# Load API key from .env
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

# Initialize client
client = genai.Client(api_key=api_key)

# Define the system prompt
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths must be relative to the working directory. Never include the working directory itself in the function call—only use the relative path.
"""

# Register available function schemas
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

# Function dispatcher
def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    args = dict(function_call_part.args)
    args["working_directory"] = "./calculator"

    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f" - Calling function: {function_name}")

    functions = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "write_file": write_file,
        "run_python_file": run_python_file,
    }

    if function_name not in functions:
        return types.Content(
            role="tool",
            parts=[types.Part.from_function_response(
                name=function_name,
                response={"error": f"Unknown function: {function_name}"}
            )]
        )

    try:
        result = functions[function_name](**args)
    except Exception as e:
        result = f"Error: {e}"

    if verbose:
        print(f"-> {result}")

    return types.Content(
        role="tool",
        parts=[types.Part.from_function_response(
            name=function_name,
            response={"result": result}
        )]
    )

# Main agent loop
def main():
    if len(sys.argv) < 2:
        print("Error: No prompt provided.")
        sys.exit(1)

    user_prompt = sys.argv[1]
    verbose = "--verbose" in sys.argv

    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

    for _ in range(20):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=[available_functions],
                ),
            )

            # Process response
            for candidate in response.candidates:
                content = candidate.content
                if content:
                    messages.append(content)

                    # If this message contains a function call
                    if content.parts and content.parts[0].function_call:
                        function_call = content.parts[0].function_call
                        function_response = call_function(function_call, verbose)
                        messages.append(function_response)
                        break  # let the next loop use updated context

                    # If it's a final message (text response)
                    if content.parts and content.parts[0].text:
                        print(content.parts[0].text)
                        if verbose:
                            print("Prompt tokens:", response.usage_metadata.prompt_token_count)
                            print("Response tokens:", response.usage_metadata.candidates_token_count)
                        return

        except Exception as e:
            print(f"Fatal error: {e}")
            break

    print("Max iterations reached. Exiting.")


if __name__ == "__main__":
    main()
