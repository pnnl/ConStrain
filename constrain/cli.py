"""
cli.py
====================================
This the command line interface module of ConStrain. Currently it is mostly used to open ConStrain's GUI.
"""

import click, sys
from .app.app import GUI
from PyQt6.QtWidgets import QApplication


@click.group()
def cli():
    """
    ConStrain

    ConStrain or Control Strainer is a data-driven knowledge-integrated framework that automatically verifies that building system controls function as intended
    """


def open_app():
    app = QApplication(sys.argv)
    window = GUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    open_app()
