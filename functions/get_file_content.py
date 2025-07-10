import os
from functions.config import MAX_CHARS
from google.genai import types
from functions.get_files_info import schema_get_files_info

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the contents of the specified file, truncated to a safe length. Path must remain within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file, relative to the working directory.",
            ),
        },
    ),
)

def get_file_content(working_directory, file_path):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

        if not abs_file_path.startswith(abs_working_dir):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(abs_file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(abs_file_path, "r", encoding="utf-8") as f:
            content = f.read(MAX_CHARS + 1)

        if len(content) > MAX_CHARS:
            content = content[:MAX_CHARS] + f' [...File "{file_path}" truncated at {MAX_CHARS} characters]'

        return content

    except Exception as e:
        return f"Error: {str(e)}"
    