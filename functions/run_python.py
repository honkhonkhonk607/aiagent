import os
import subprocess
from google.genai import types
from functions.get_files_info import schema_get_files_info

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file and returns stdout and stderr. File must end in .py and reside within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to execute, relative to the working directory.",
            ),
        },
    ),
)

def run_python_file(working_directory, file_path):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

        if not abs_file_path.startswith(abs_working_dir):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(abs_file_path):
            return f'Error: File "{file_path}" not found.'

        if not abs_file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        result = subprocess.run(
            ["python", abs_file_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=abs_working_dir,
        )

        output_parts = []
        if result.stdout:
            output_parts.append(f"STDOUT:\n{result.stdout.strip()}")
        if result.stderr:
            output_parts.append(f"STDERR:\n{result.stderr.strip()}")
        if result.returncode != 0:
            output_parts.append(f"Process exited with code {result.returncode}")

        return "\n".join(output_parts) if output_parts else "No output produced."

    except Exception as e:
        return f"Error: executing Python file: {e}"
    