from os import makedirs, environ, pathsep, path, getcwd
from pathlib import Path
from shutil import rmtree
from requests import get
from remotezip import RemoteZip
from base64 import b64decode

from deps.app_utils import Color


def base64_to_file(base64_code, output_dir, output_filename) -> None:
    """
    Converts a base64 code to a file
    :param base64_code: The base64 code
    :param output_dir: The output directory
    :param output_filename: The output name
    :return: None
    """

    if not Path(output_dir, output_filename).is_file():
        with open(Path(output_dir, output_filename), 'wb') as file:
            file.write(b64decode(base64_code))


def application_dirs(app_main_dir) -> None:
    """
    Creates the application directories
    :return: None
    """

    # Internal directories
    makedirs(Path(f'{app_main_dir}', 'deps'), exist_ok=True)
    makedirs(Path(f'{app_main_dir}', 'assets'), exist_ok=True)
    makedirs(Path(f'{app_main_dir}', '.temp'), exist_ok=True)

    # Output directories
    makedirs(Path('songs'), exist_ok=True)


def application_ffmpeg(app_dependencies_dir) -> None:
    """
    Download the FFMPEG dependency
    :return: None
    """

    if not Path(f'{app_dependencies_dir}/ffmpeg.exe').is_file():
        print(f'\n{Color.WHITE}★ FFMPEG is not installed, downloading...', end='\r')

        repo = 'https://github.com/GyanD/codexffmpeg/releases/latest'

        latest_ffmpeg = get(repo).url.rsplit('/', 1)[-1]
        build = f'ffmpeg-{latest_ffmpeg}-essentials_build'

        with RemoteZip(f'{repo}/download/{build}.zip') as rzip:
            total_size = rzip.getinfo(f'{build}/bin/ffmpeg.exe').compress_size

            rzip.extract(f'{build}/bin/ffmpeg.exe', Path(app_dependencies_dir))
            Path(f'{app_dependencies_dir}/{build}/bin/ffmpeg.exe').rename(
                Path(f'{app_dependencies_dir}/ffmpeg.exe')
            )
            rmtree(Path(f'{app_dependencies_dir}/{build}'), ignore_errors=True)

            print(
                f'{Color.WHITE}★ FFMPEG was successfully downloaded! (Compressed: {total_size / 1024 / 1024:.2f} MB & '
                f'Uncompressed: {rzip.getinfo(f"{build}/bin/ffmpeg.exe").file_size / 1024 / 1024:.2f} MB)'
            )
    environ['PATH'] += pathsep + path.join(getcwd(), Path(app_dependencies_dir))
