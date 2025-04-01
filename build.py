import subprocess
import os


def build_wizard_executable():
    gui_path = "tools/wizard/main.py"
    schema_dir = "schema"

    command = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        f"--add-data={os.path.join(schema_dir, 'library.json')}:{schema_dir}",
        gui_path,
    ]

    subprocess.run(command, check=True)


if __name__ == "__main__":
    build_wizard_executable()
