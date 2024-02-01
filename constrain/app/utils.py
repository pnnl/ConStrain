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


def send_are_you_sure(text):
    """Displays an 'are you sure' message with given text

    Args:
        text (str): text to be displayed
    """
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Question)
    msg_box.setText(f"Are you sure? {text}")
    msg_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    msg_box.setWindowTitle("ConStrain")
    response = msg_box.exec()
    return response
