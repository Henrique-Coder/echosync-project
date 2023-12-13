from PyQt6 import QtCore, QtGui, QtWidgets
from sys import argv, exit
from pathlib import Path

from assets.app_functions import pyqt_setup, pyqt_utils as qtu, apputils as apu


def main_app(ui: pyqt_setup.Ui_echosync_project) -> None:
    # Set window icon
    EchoSyncProject.setWindowIcon(QtGui.QIcon(apu.get_fullpath_string('icon.ico')))

    # Set "btnImportFromFile" icon and icon size
    ui.btnImportFromFile.setIcon(QtGui.QIcon(apu.get_fullpath_string('assets/images/explorer.png')))
    ui.btnImportFromFile.setIconSize(QtCore.QSize(20, 20))

    # Action: Import from file
    def import_queries_from_file() -> None:
        file_path = qtu.open_filedialog(EchoSyncProject, 'Import queries from file',
                                        apu.get_fullpath_string(Path.cwd()), 'Text and CSV files (*.txt *.csv)')

        if not file_path:
            return

        file_delimiter = '.txt'
        file_extension = file_path.suffix

        if file_extension == '.txt':
            file_delimiter = '\n'
        elif file_extension == '.csv':
            file_delimiter = ','

        file_query_list = apu.read_from_file(file_path, file_delimiter)

        if not file_query_list:
            return

        input_queries = set(query.strip() for query in ui.inputUrlList.toPlainText().split('\n') if query.strip())
        file_query_list = set(map(str.strip, file_query_list))
        new_queries = sorted(input_queries | file_query_list)

        formatted_queries = '\n'.join(new_queries)
        qtu.set_label_text(ui.inputUrlList, formatted_queries)

    ui.btnImportFromFile.clicked.connect(import_queries_from_file)

    # Action: Go to progress window
    def goto_progress_window() -> None:
        qtu.show_widget(ui.downloadProgress)

    ui.btnNext.clicked.connect(goto_progress_window)


if __name__ == '__main__':
    app = QtWidgets.QApplication(argv)
    EchoSyncProject = QtWidgets.QMainWindow()
    ui = pyqt_setup.Ui_echosync_project()
    ui.setupUi(EchoSyncProject)
    main_app(ui)
    qtu.show_widget(EchoSyncProject)
    exit(app.exec())
