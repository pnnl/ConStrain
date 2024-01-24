from PyQt6.QtWidgets import QMessageBox


def send_error(window_title, text):
    """Displays an error message with given text

    Args:
        text (str): text to be displayed
    """
    error_msg = QMessageBox()
    error_msg.setIcon(QMessageBox.Icon.Critical)
    error_msg.setWindowTitle(window_title)
    error_msg.setText(text)
    error_msg.exec()
