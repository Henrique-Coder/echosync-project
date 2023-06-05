from requests import get, ConnectionError
from colorama import Fore
from subprocess import run
from re import sub


class Color:
    RED = Fore.LIGHTRED_EX
    WHITE = Fore.LIGHTWHITE_EX
    GREEN = Fore.LIGHTGREEN_EX
    BLUE = Fore.LIGHTBLUE_EX
    YELLOW = Fore.LIGHTYELLOW_EX
    CYAN = Fore.LIGHTCYAN_EX
    MAGENTA = Fore.LIGHTMAGENTA_EX


def is_internet_connected() -> bool:
    """
    Checks if the internet is connected
    :return: True if connected, False if not
    """

    try:
        response = get('http://www.google.com', timeout=5)

        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


def app_update_checker(app_version) -> None:
    """
    Checks if the application is up to date
    :return: None
    """

    repo_releases = 'https://github.com/Henrique-Coder/batch-music-downloader/releases'
    repo_latest = f'{repo_releases}/latest'
    latest_version = get(repo_latest).url.rsplit('/', 1)[-1].replace('v', '')

    if latest_version > app_version:
        print(
            f'\n{Color.MAGENTA}★ This app version is out of date ({app_version}), '
            f'the latest available version is {latest_version}!'
        )
        print(f'{Color.MAGENTA}★ Download it at: {repo_releases}/tag/v{latest_version}')


def clsr(jump_lines: int = 0) -> None:
    """
    Clears the terminal screen and other stuff
    :param jump_lines: optional, number of blank lines to be skipped after clearing the screen
    :return: None
    """

    run('cls || clear', shell=True)

    for i in range(jump_lines):
        print()


def format_seconds_to_time(seconds: int) -> str:
    """
    Converts seconds to a formatted string in the format 'hh:mm:ss'
    :param seconds: required, seconds to be converted
    :return: formatted time (hh:mm:ss)
    """

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    hours_str = str(hours).zfill(2)
    minutes_str = str(minutes).zfill(2)
    seconds_str = str(seconds).zfill(2)

    return f'{hours_str}:{minutes_str}:{seconds_str}'


def fix_string(string: str) -> str:
    """
    Format the string to be compatible with all operating systems
    :param string: required, string to be formatted
    :return: formatted string
    """

    # Format the string to be compatible with all operating systems
    new_string = str()
    allowed_chars = (
        'aáàâãbcçdeéèêfghiíìîjklmnoóòôõpqrstuúùûvwxyzAÁÀÂÃBCÇDEÉÈÊFGHIÍÌÎJKLMNOÓÒÔÕPQRSTUÚÙÛVWXYZ'
        '0123456789-_()[]{}# '
    )

    for char in string:
        if char in allowed_chars:
            new_string += char

    return sub(' +', ' ', new_string).strip()
