from base64 import b64decode
from pathlib import Path
from shutil import rmtree
from subprocess import run
from tkinter import Tk, filedialog
from typing import Optional
from colorama import init, Fore
from remotezip import RemoteZip
from httpx import get, head


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
        return '\n' * self.jump_lines + f'{TerminalTextColors.WHITE}[{self.color}{self.text}{TerminalTextColors.WHITE}]'


def init_colorama(autoreset: bool = True) -> None:
    """
    Initialize colorama module
    :param autoreset:  Reset color after print
    :return:  None
    """

    init(autoreset=autoreset)


def clsr(jump_lines: int = 0) -> None:
    """
    Clear terminal screen
    :param jump_lines:  Number of lines to jump after clear
    :return:  None
    """

    run('cls || clear', shell=True)

    for _ in range(jump_lines):
        print()


def is_app_updated(app_version: str, github_repository_owner: str, github_repository_name: str) -> tuple:
    """
    Check if app is updated
    :param app_version:  App version
    :param github_repository_owner:  GitHub repository owner
    :param github_repository_name:  GitHub repository name
    :return:  Tuple with boolean value, latest version available and latest release url
    """

    api_url = f'https://api.github.com/repos/{github_repository_owner}/{github_repository_name}/releases/latest'
    gh_data = get(api_url).json()

    latest_version_available = gh_data['tag_name'].replace('v', str())
    latest_release_url = gh_data['html_url']

    is_updated = latest_version_available <= app_version

    return is_updated, latest_version_available, latest_release_url


def base64_decoder(base64_data: str, output_file_path: Path) -> None:
    """
    Decode base64 data and save it to file
    :param base64_data:  Base64 data
    :param output_file_path:  Output file path
    :return:  None
    """

    output_file_path.write_bytes(b64decode(base64_data))


def create_dirs(main_dir: Path, dir_list: list) -> None:
    """
    Create main directory and subdirectories
    :param main_dir:  Main directory
    :param dir_list:  List of subdirectories to create
    :return:  None
    """

    for directory in dir_list:
        Path(main_dir, directory).mkdir(parents=True, exist_ok=True)


def hide_windows_folder(folder_path: Path) -> None:
    """
    Hide Windows folder from explorer
    :param folder_path:  Folder path to hide
    :return:  None
    """

    run(f'attrib +h "{folder_path}"', shell=True)


def download_latest_ffmpeg(output_file_dir: Path, file_name: str = 'ffmpeg') -> None:
    """
    Download latest ffmpeg build from official GitHub repository
    :param output_file_dir:  Output file directory
    :param file_name:  File name (without extension)
    :return:  None
    """

    github_repository_owner = 'GyanD'
    github_repository_name = 'codexffmpeg'

    api_url = f'https://api.github.com/repos/{github_repository_owner}/{github_repository_name}/releases/latest'
    gh_data = get(api_url).json()

    github_repository = f'https://github.com/{github_repository_owner}/{github_repository_name}'
    build_name = f'ffmpeg-{gh_data["tag_name"]}-essentials_build'

    with RemoteZip(f'{github_repository}/releases/latest/download/{build_name}.zip') as rzip:
        rzip.extract(f'{build_name}/bin/{file_name}.exe', output_file_dir)

        Path(f'{output_file_dir}/{build_name}/bin/{file_name}.exe').rename(Path(f'{output_file_dir}/{file_name}.exe'))
        rmtree(Path(f'{output_file_dir}/{build_name}'), ignore_errors=True)


def filedialog_selector(window_title: str, window_icon_path: Path, allowed_file_types: list) -> Optional[Path]:
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
    input_file_path = filedialog.askopenfilename(title=window_title, filetypes=allowed_file_types)

    # Destroys the dialog window
    tkroot.destroy()

    # Returns the selected file path if it has been selected, otherwise returns None
    if not input_file_path:
        return None

    return Path(input_file_path)


def unshorten_url(short_url: str) -> str:
    """
    Get final link from short url
    :param short_url:  Short url
    :return:  Unshortened url
    """

    try:
        unshortened_url = head(short_url, follow_redirects=True).url
    except Exception:
        unshortened_url = short_url

    return unshortened_url
