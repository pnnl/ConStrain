"""
This scripts auto-generate the documentationfor verifications included in the library
"""

import json

LIBRARY_PATH = "../../schema/library.json"


def upper_case_all_words(words):
    upper_case_words = []
    for word in words:
        upper_case_words.append(f"{word[0].upper()}{word[1:]}")
    return upper_case_words


def generate_verification_docs():
    lib = json.load(open(LIBRARY_PATH, "r"))
    main_doc_page = open("./Verifications.rst", "w")
    main_doc_page.write("Verifications\n===============\n\n")
    main_doc_page.write(
        "Listed below are all the verification currently implemented in ConStrain.\n\n"
    )
    main_doc_page.write(".. toctree::\n")
    main_doc_page.write("   :maxdepth: 1\n\n")
    for verification, verification_info in lib.items():
        main_doc_page.write(f"   {verification}\n")
        verification_documentation = open(f"./{verification}.rst", "w")
        verification_documentation.write(f"{verification}\n")
        verification_documentation.write(
            "====================================================================\n\n"
        )
        for k in verification_info.keys():
            # skip IDs
            if "id" not in k:
                subtitle_words = k.split("_")
                # inverse description
                if "description" in subtitle_words:
                    subtitle_words.reverse()
                verification_documentation.write(
                    f"{' '.join(upper_case_all_words(subtitle_words))}\n"
                )
                verification_documentation.write(
                    "-------------------------------------------------------------------------------\n"
                )
                content = verification_info[k]
                if isinstance(content, list):
                    for i in range(len(content)):
                        verification_documentation.write(f"   * {content[i]}\n\n")
                elif isinstance(content, dict):
                    for k, v in content.items():
                        verification_documentation.write(f"   * {k}: {content[k]}\n")
                    verification_documentation.write("\n")
                else:
                    verification_documentation.write(f"{content.capitalize()}\n\n")


if __name__ == "__main__":
    generate_verification_docs()
