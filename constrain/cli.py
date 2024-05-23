"""
cli.py
====================================
This the command line interface module of ConStrain. Currently it is mostly used to open ConStrain's GUI.
"""

import click, sys
from .app.views.main_window import MainWindow
from PyQt6.QtWidgets import QApplication


@click.group()
def cli():
    """
    ConStrain

    ConStrain or Control Strainer is a data-driven knowledge-integrated framework that automatically verifies that building system controls function as intended
    """
    pass


@cli.command()
def open():
    """Open the ConStrain GUI."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    cli()
