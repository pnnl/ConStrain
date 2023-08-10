import ast
import inspect
import re


def extract_method_info(node):
    if not isinstance(node, ast.FunctionDef):
        return None

    method_info = {
        "name": node.name,
        "description": ast.get_docstring(node),
    }

    return method_info


def extract_class_info(node):
    if not isinstance(node, ast.ClassDef):
        return None

    class_info = {"class": node.name, "methods": []}

    for item in node.body:
        if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
            method_info = extract_method_info(item)
            if method_info:
                class_info["methods"].append(method_info)

    return class_info


def parse_python_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    tree = ast.parse(content)
    classes = []

    for item in tree.body:
        if isinstance(item, ast.ClassDef):
            class_info = extract_class_info(item)
            if class_info:
                classes.append(class_info)

    return classes


def parse_python_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    tree = ast.parse(content)
    classes = []

    for item in tree.body:
        if isinstance(item, ast.ClassDef):
            class_info = extract_class_info(item)
            if class_info:
                classes.append(class_info)

    return classes


if __name__ == "__main__":
    python_file_path = (
        "C:\\Users\\slan572\\includes_gui\\ConStrain\\src\\api\\data_processing.py"
    )

    python_file_paths = [
        "C:\\Users\\slan572\\includes_gui\\ConStrain\\src\\api\\data_processing.py",
        "C:\\Users\\slan572\\includes_gui\\ConStrain\\src\\api\\reporting.py",
        "C:\\Users\\slan572\\includes_gui\\ConStrain\\src\\api\\verification_case.py",
        "C:\\Users\\slan572\\includes_gui\\ConStrain\\src\\api\\verification_library.py",
        "C:\\Users\\slan572\\includes_gui\\ConStrain\\src\\api\\verification.py",
    ]

    all_dict = {}

    for p in python_file_paths:
        extracted_classes = parse_python_file(p)
        for class_info in extracted_classes:
            class_name = class_info["class"]
            all_dict[class_name] = {}

            for method in class_info["methods"]:
                method_name = method["name"]
                if "verification_case.py" in p:
                    print(method_name)
                all_dict[class_name][method_name] = []
                # print(method["name"])
                # print(method["description"].split("\n\nArgs:\n    "))
                try:
                    description, arg_descriptions = method["description"].split(
                        "\n\nArgs:\n    "
                    )

                    try:
                        (
                            arg_descriptions,
                            return_descriptions,
                        ) = arg_descriptions.split("\n\n")
                    except ValueError:
                        return_descriptions = ""
                except ValueError:
                    try:
                        description, return_descriptions = method["description"].split(
                            "\n\nReturns:\n"
                        )
                        arg_descriptions = ""
                    except ValueError:
                        break

                if "verification_case.py" in p:
                    print(arg_descriptions)

                if arg_descriptions:
                    pattern = r"^(.*?)\((.*?)\): (.*?)$"
                    arg_descriptions = arg_descriptions.split("\n    ")
                    for arg in arg_descriptions:
                        match = re.search(pattern, arg, re.MULTILINE)
                        if match:
                            name = match.group(1).strip()
                            types = match.group(2).strip()
                            des = match.group(3).strip()

                            # print(method_name)
                            all_dict[class_name][method_name].append(
                                {"label": name, "type": types, "description": des}
                            )
                        else:
                            all_dict[class_name].pop(method_name)
                            break
                if return_descriptions:
                    return_descriptions = return_descriptions.split("\n    ")
                    # print(return_descriptions, "\n")
                # print(method_descriptions.split("\n    "))
            # print(method_descriptions, return_descriptions)
    # print(all_dict)
