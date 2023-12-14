from PyQt6 import QtCore, QtGui, QtWidgets
from sys import argv, exit
from pathlib import Path
from yt_dlp import YoutubeDL
from youtubesearchpython import SearchVideos
from subprocess import Popen
from unicodedata import normalize
from re import sub
from music_tag import load_file

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
        def sort_links(query_list: list) -> dict:
            query_dict = {'links': list(), 'titles': list()}

            ui.pbSortingLinks.setValue(0)
            for query in query_list:
                ui.pbSortingLinks.setValue(int((query_list.index(query) + 1) / len(query_list) * 100))
                if query.startswith('http'):
                    query_dict['links'].append(query)
                else:
                    query_dict['titles'].append(query)

            ui.pbSortingLinks.setValue(100)

            return query_dict

        def search_songs_by_title(query_dict: dict) -> list:
            url_query_list = list()

            ui.pbSearchingURLsByTitle.setValue(0)

            for query in query_dict['titles']:
                query_url = str(SearchVideos(query, offset=1, mode='dict', max_results=1).result()['search_result'][0]['link'])
                url_query_list.append(query_url)
                ui.pbSearchingURLsByTitle.setValue(int((query_dict['titles'].index(query) + 1) / len(query_dict['titles']) * 100))

            ui.pbSearchingURLsByTitle.setValue(100)

            url_query_list.extend(query_dict['links'])

            return url_query_list

        def download_song(url_query_list: list) -> None:
            ui.pbDownloadingSongsByUrl.setValue(0)

            Path(Path.cwd(), 'songs').mkdir(parents=True, exist_ok=True)

            def fix_title(title: str) -> str:
                normalized_title = normalize('NFKD', title).encode('ASCII', 'ignore').decode('utf-8')
                sanitized_title = sub(r'\s+', ' ', sub(r'[^a-zA-Z0-9\-_()[\]{}# ]', str(), normalized_title).strip())

                return sanitized_title

            ydl_opts_info = {
                'quiet': True,
                'no_warnings': True,
            }

            for url in url_query_list:
                song_info = YoutubeDL(ydl_opts_info).extract_info(url, download=False)
                output_file_path_wo_ext = Path(Path.cwd(), 'songs', fix_title(song_info['title']))
                temp_output_file_path_wo_ext = Path(f'{output_file_path_wo_ext}-temp')

                ydl_opts_download = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{temp_output_file_path_wo_ext}.opus',
                    'quiet': True,
                    'no_warnings': True,
                    'nooverwrites': True,
                }

                with YoutubeDL(ydl_opts_download) as ydl:
                    ydl.download([url])

                temp_output_file_path = Path(f'{temp_output_file_path_wo_ext}.opus').absolute()
                output_file_path = Path(f'{output_file_path_wo_ext}.opus').absolute()

                ffmpeg_proc = Popen(f'"assets/binaries/ffmpeg/ffmpeg.exe" -i "{temp_output_file_path}" -c:a libopus -b:a 192k -y -hide_banner -loglevel quiet "{output_file_path}"', shell=True)
                ffmpeg_proc.wait()

                temp_output_file_path.unlink(missing_ok=True)

                f = load_file(output_file_path)
                f['tracktitle'] = fix_title(song_info['title'])
                f['artist'] = song_info['uploader']
                f['year'] = song_info['upload_date'][:4]
                f.save()

                ui.pbDownloadingSongsByUrl.setValue(int((url_query_list.index(url) + 1) / len(url_query_list) * 100))

            ui.pbDownloadingSongsByUrl.setValue(100)

        if not ui.inputUrlList.toPlainText().strip():
            return

        qtu.show_widget(ui.downloadProgress)

        ui.pbSortingLinks.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        query_dict = sort_links(ui.inputUrlList.toPlainText().split('\n'))
        ui.pbSortingLinks.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

        ui.pbSearchingURLsByTitle.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        url_query_list = search_songs_by_title(query_dict)
        ui.pbSearchingURLsByTitle.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

        EchoSyncProject.setFixedSize(600, 255)
        ui.pbDownloadingSongsByUrl.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        download_song(url_query_list)
        ui.inputUrlList.clear()
        ui.inputUrlList.setFocus()
        ui.pbDownloadingSongsByUrl.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        EchoSyncProject.setFixedSize(600, 410)

        qtu.hide_widget(ui.downloadProgress)

    ui.btnNext.clicked.connect(goto_progress_window)


if __name__ == '__main__':
    app = QtWidgets.QApplication(argv)
    EchoSyncProject = QtWidgets.QMainWindow()
    ui = pyqt_setup.Ui_echosync_project()
    ui.setupUi(EchoSyncProject)
    main_app(ui)
    qtu.show_widget(EchoSyncProject)
    exit(app.exec())
