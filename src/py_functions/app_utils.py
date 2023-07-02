from base64 import b64decode
from pathlib import Path
from shutil import rmtree
from subprocess import run
from tkinter import Tk, filedialog
from typing import Optional
from colorama import init, Fore
from remotezip import RemoteZip
from requests import get
from time import time


class Timer:
    """
    Timer class (for debugging)
    """

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self) -> None:
        """
        Start timer
        :return:
        """

        self.start_time = time()

    def stop(self) -> None:
        """
        Stop timer
        :return:
        """

        self.end_time = time()

    def get_time(self) -> float:
        """
        Get time
        :return:  Time
        """

        return self.end_time - self.start_time


class TerminalTextColors:
    """
    Terminal text colors
    """

    RED = Fore.RED
    WHITE = Fore.WHITE
    GREEN = Fore.GREEN
    BLUE = Fore.BLUE
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA

    LRED = Fore.LIGHTRED_EX
    LWHITE = Fore.LIGHTWHITE_EX
    LGREEN = Fore.LIGHTGREEN_EX
    LBLUE = Fore.LIGHTBLUE_EX
    LYELLOW = Fore.LIGHTYELLOW_EX
    LCYAN = Fore.LIGHTCYAN_EX
    LMAGENTA = Fore.LIGHTMAGENTA_EX


class TerminalCustomBrackets(TerminalTextColors):
    """
    Custom terminal brackets
    """

    def __init__(self, color, text, jump_lines: int = 0):
        self.color = color
        self.text = text
        self.jump_lines = jump_lines

    def __str__(self):
        return (
            '\n' * self.jump_lines
            + f'{TerminalTextColors.WHITE}[{self.color}{self.text}{TerminalTextColors.WHITE}]'
        )


def init_colorama(autoreset: bool = True) -> None:
    """
    Initialize colorama module
    :param autoreset:  Reset color after print
    :return:
    """

    init(autoreset=autoreset)


def clsr(jump_lines: int = 0) -> None:
    """
    Clear terminal screen
    :param jump_lines:  Number of lines to jump after clear
    :return:
    """

    run('cls || clear', shell=True)

    for _ in range(jump_lines):
        print()


def is_internet_connected(host, timeout) -> bool:
    """
    Check if internet is connected
    :param host:  Host to check
    :param timeout:  Limit time to check
    :return: True if connected, False if not
    """

    try:
        response = get(host, timeout=timeout)
        if response.status_code == 200:
            return True
    except Exception:
        return False


def is_app_updated(app_version, github_repository) -> tuple:
    """
    Check if app is updated
    :param app_version:  App version
    :param github_repository:  Github repository
    :return:
    """

    github_latest_repository = github_repository + '/releases/latest'
    latest_version_available = (
        get(github_latest_repository).url.rsplit('/', 1)[-1].replace('v', '')
    )
    lastest_release_url = (
        f'{github_repository}/releases/tag/v{latest_version_available}'
    )

    if latest_version_available > app_version:
        is_updated = False
    else:
        is_updated = True
    return is_updated, latest_version_available, lastest_release_url


def base64_decoder(base64_data, output_file_path) -> None:
    """
    Decode base64 data to file
    :param base64_data:  Base64 data
    :param output_file_path:  Output file path
    :return:
    """

    output_file_path.write_bytes(b64decode(base64_data))


def create_dirs(main_dir, dirs_list: list) -> None:
    """
    Create directories
    :param main_dir:  Main directory
    :param dirs_list:  List of directories to create
    :return:
    """

    for directory in dirs_list:
        Path(main_dir, directory).mkdir(parents=True, exist_ok=True)


def download_latest_ffmpeg(output_file_dir, file_name) -> None:
    """
    Download latest ffmpeg build
    :param output_file_dir:  Output file directory
    :param file_name:  File name
    :return:
    """

    github_repository = 'https://github.com/GyanD/codexffmpeg'
    latest_official_version = get(github_repository + '/releases/latest').url.rsplit(
        '/', 1
    )[-1]
    build_name = f'ffmpeg-{latest_official_version}-essentials_build'

    with RemoteZip(
        f'{github_repository}/releases/latest/download/{build_name}.zip'
    ) as rzip:
        rzip.extract(f'{build_name}/bin/{file_name}.exe', output_file_dir)

        Path(f'{output_file_dir}/{build_name}/bin/{file_name}.exe').rename(
            Path(f'{output_file_dir}/{file_name}.exe')
        )

        rmtree(Path(f'{output_file_dir}/{build_name}'), ignore_errors=True)


def filedialog_selector(window_title: str, window_icon_path, allowed_file_types: list) -> Optional[Path]:
    """
    File dialog selector
    :param window_title:  Window title
    :param window_icon_path:  Window icon path
    :param allowed_file_types:  Allowed file types
    :return:  Selected file path or None
    """

    # Creates and configures a dialog window
    tkroot = Tk()
    tkroot.withdraw()
    tkroot.attributes('-topmost', True)
    tkroot.title(window_title)
    tkroot.iconbitmap(Path(window_icon_path))
    tkroot.update()

    # Opens a dialog window for selecting the input file
    input_file_path = filedialog.askopenfilename(
        title=window_title, filetypes=allowed_file_types
    )

    # Destroys the dialog window
    tkroot.destroy()

    # Returns the selected file path if it has been selected, otherwise returns None
    if not input_file_path:
        return None
    return Path(input_file_path)
