import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

def get_files_info(working_directory, directory=None):
    if directory is None:
        full_path = working_directory
        relative_path = "."
    else:
        full_path = os.path.join(working_directory, directory)
        relative_path = directory

    try:
        full_path = os.path.abspath(full_path)
        working_directory = os.path.abspath(working_directory)

        if not full_path.startswith(working_directory):
            return f'Error: Cannot list "{relative_path}" as it is outside the permitted working directory'

        if not os.path.isdir(full_path):
            return f'Error: "{relative_path}" is not a directory'

        entries = os.listdir(full_path)
        results = []

        for entry in entries:
            try:
                entry_path = os.path.join(full_path, entry)
                is_dir = os.path.isdir(entry_path)
                size = os.path.getsize(entry_path)
                results.append(
                    f"- {entry}: file_size={size} bytes, is_dir={is_dir}"
                )
            except Exception as e:
                results.append(f"- {entry}: Error: {str(e)}")

        return "\n".join(results)

    except Exception as e:
        return f"Error: {str(e)}"
