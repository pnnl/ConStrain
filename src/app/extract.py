import ast
import re
import json


def extract_method_info(node):
    """Retrieves method info from node

    Args:
        node (ast.FunctionDef): method to use

    Returns:
        dict: dictionary containing keys "name" and "description"
    """
    if not isinstance(node, ast.FunctionDef):
        return None

    method_info = {
        "name": node.name,
        "description": ast.get_docstring(node),
    }

    return method_info


def extract_class_info(node):
    """Retrieves class info from node

    Args:
        node (ast.ClassDef): class to use

    Returns:
        list: list of method info dictionaries from a class
    """
    if not isinstance(node, ast.ClassDef):
        return None

    class_info = {"class": node.name, "methods": []}

    for item in node.body:
        if isinstance(item, ast.FunctionDef) and (
            not item.name.startswith("_") or item.name == "__init__"
        ):
            method_info = extract_method_info(item)
            # print(method_info)
            if method_info:
                class_info["methods"].append(method_info)

    return class_info


def parse_python_file(file_path):
    """Given a file path, reads contents to find each class in file

    Args:
        file_path (str): file path to read

    Returns:
        list: list of class info lists
    """
    with open(file_path, "r") as file:
        content = file.read()

    tree = ast.parse(content)
    classes = []

    for item in tree.body:
        if isinstance(item, ast.ClassDef):
            class_info = extract_class_info(item)
            print(class_info)
            if class_info:
                classes.append(class_info)

    return classes


def format_method_name(method_name: str):
    """Formats an API-formatted method name into a method name to be displayed in the GUI

    Args:
        method_name (str): method name to format

    Returns:
        str: formatted method name
    """
    if method_name == "__init__":
        return "Initialize"

    method_name = method_name.replace("_", " ")
    method_name = method_name.title()
    method_name = method_name.replace("Json", "JSON")
    method_name = method_name.replace("Ids", "IDs")

    uncap = ["To", "By", "From"]
    for w in uncap:
        method_name = method_name.replace(w, w.lower())

    return method_name


def place_args(arg_descriptions):
    """Places the argument names, their types, and their descriptions inside a dictionary

    Args:
        arg_descriptions (list): arg_descriptions for a method inside of a class
    """
    pattern = r"^(.*?)\((.*?)\): (.*?)$"
    arg_descriptions = arg_descriptions.split("\n    ")
    for arg in arg_descriptions:
        match = re.search(pattern, arg, re.MULTILINE)
        if match:
            name = match.group(1).strip()
            types = match.group(2).strip()
            des = match.group(3).strip()

            if "optional" in types:
                name += " - Optional"
                types = types.split(", optional")[0]

            if types == "bool":
                types = "combo_box"
            else:
                types = "line_edit"

            all_dict[class_name][method_name].append(
                {"label": format_method_name(name), "type": types, "description": des}
            )
        else:
            continue


# Parses, extracts, puts extractions into dictionary, converts to .json
if __name__ == "__main__":
    python_file_paths = [
        "C:\\Users\\slan572\\scrapes\\ConStrain\\src\\api\\data_processing.py",
        "C:\\Users\\slan572\\scrapes\\ConStrain\\src\\api\\reporting.py",
        "C:\\Users\\slan572\\scrapes\\ConStrain\\src\\api\\verification_case.py",
        "C:\\Users\\slan572\\scrapes\\ConStrain\\src\\api\\verification_library.py",
        "C:\\Users\\slan572\\scrapes\\ConStrain\\src\\api\\verification.py",
    ]

    all_dict = {}

    for p in python_file_paths:
        extracted_classes = parse_python_file(p)
        for class_info in extracted_classes:
            class_name = class_info["class"]
            all_dict[class_name] = {}

            for method in class_info["methods"]:
                method_name = method["name"]
                method_name = format_method_name(method_name)

                all_dict[class_name][method_name] = []
                try:
                    description, arg_descriptions = method["description"].split(
                        "\n\nArgs:\n    "
                    )

                    try:
                        (
                            arg_descriptions,
                            return_descriptions,
                        ) = arg_descriptions.split("\n\n", 1)
                    except ValueError:
                        return_descriptions = ""
                except ValueError:
                    try:
                        description, return_descriptions = method["description"].split(
                            "\n\nReturns:\n"
                        )
                        arg_descriptions = ""
                    except ValueError:
                        description, return_descriptions, arg_descriptions = (
                            method["description"],
                            "",
                            "",
                        )

                if arg_descriptions:
                    place_args(arg_descriptions)

    with open("schema.json", "w") as json_file:
        json.dump(all_dict, json_file, indent=4)
