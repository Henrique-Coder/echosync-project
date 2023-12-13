from PyQt6 import QtCore, QtGui, QtWidgets
from pathlib import Path
from typing import Any, Union


def hide_widget(widget: QtWidgets.QWidget) -> None:
    widget.hide()
    widget.raise_()


def show_widget(widget: QtWidgets.QWidget) -> None:
    widget.show()
    widget.raise_()


def open_filedialog(class_name: QtWidgets.QMainWindow, window_title: str, default_dir: str = str(Path.cwd()), file_filter: str = 'All files (*.*)') -> Union[Path, None]:
    user_input = QtWidgets.QFileDialog.getOpenFileName(class_name, window_title, default_dir, file_filter)[0]

    if not user_input or not Path(user_input).is_file():
        return None

    return Path(user_input).absolute()


def set_label_text(label: QtWidgets, text: str) -> None:
    label.setText(text.strip())
