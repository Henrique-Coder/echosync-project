from os import makedirs, environ, pathsep, path, getcwd, remove
from pathlib import Path
from re import sub, findall
from shutil import rmtree
from subprocess import run as subrun
from time import sleep, time
from tkinter import Tk, filedialog
from bs4 import BeautifulSoup
from colorama import init as colorama_init, Fore
from music_tag import load_file as tag_load_file
from pytube import YouTube, Playlist, extract
from pytube.exceptions import VideoUnavailable, AgeRestrictedError, LiveStreamError, VideoPrivate, \
    RecordingUnavailable, MembersOnly, VideoRegionBlocked
from requests import get, ConnectionError
from youtubesearchpython import SearchVideos
from remotezip import RemoteZip


# Enables colors in the terminal
colorama_init(autoreset=True)

# Set the colors and decrease the size of the variables
LRED = Fore.LIGHTRED_EX
LWHITE = Fore.LIGHTWHITE_EX
LGREEN = Fore.LIGHTGREEN_EX
LBLUE = Fore.LIGHTBLUE_EX
LYELLOW = Fore.LIGHTYELLOW_EX
LCYAN = Fore.LIGHTCYAN_EX
LMAGENTA = Fore.LIGHTMAGENTA_EX

# Application version
app_version = '1.0.5'

# Creating initial variables
ext = 'mp3'

# Creating variables for the program directory
app_name = 'Batch Music Downloader [by Henrique-Coder]'
app_dir = Path(environ['userprofile'] + fr'/AppData/Local/{app_name}')
temp_dir = Path(fr'{app_dir}/.temp')


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

def app_update_checker() -> None:
    """
    Checks if the application is up to date
    :return: None
    """

    repo_releases = 'https://github.com/Henrique-Coder/batch-music-downloader/releases'
    repo_latest = f'{repo_releases}/latest'
    latest_version = get(repo_latest).url.rsplit('/', 1)[-1].replace('v', '')

    if latest_version > app_version:
        print(f'\n{LMAGENTA}★ This app is out of date ({app_version}), '
              f'the latest available version is {latest_version}!')
        print(f'{LMAGENTA}★ Download it at: {repo_releases}/tag/v{latest_version}')

def cl(jump_lines: int = 0) -> None:
    """
    Clears the terminal screen and other stuff
    :param jump_lines: optional, number of blank lines to be skipped after clearing the screen
    :return: None
    """

    subrun('cls || clear', shell=True)

    for i in range(jump_lines):
        print()

def seconds_to_time(seconds: int) -> str:
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

    formatted_time = str(f'{hours_str}:{minutes_str}:{seconds_str}')
    return formatted_time

def dep_download_assets() -> None:
    """
    Download the application assets (tiny things)
    :return: None
    """

    # Creating variables for the GitHub repository
    github_repo_url = 'https://raw.githubusercontent.com/Henrique-Coder/batch-music-downloader/main'

    # Creates the application directory if it doesn't exist
    makedirs(Path(f'{app_dir}/dependencies'), exist_ok=True)

    # Starts the Tkinter window and hides it
    root = Tk()
    root.withdraw()

    # Download the application favicon
    favicon_url = f'{github_repo_url}/favicon.ico'
    favicon_dir = Path(f'{app_dir}/favicon.ico')

    if not Path(favicon_dir).is_file():
        r = get(favicon_url, allow_redirects=True)

        with open(favicon_dir, 'wb') as fo:
            fo.write(r.content)

    # Download the dialog window icon if it doesn't exist
    makedirs(Path(f'{app_dir}/assets'), exist_ok=True)

    explorer_icon_url = f'{github_repo_url}/online_assets/explorer.ico'
    explorer_icon_dir = Path(f'{app_dir}/assets/explorer.ico')

    if not Path(explorer_icon_dir).is_file():
        r = get(explorer_icon_url, allow_redirects=True)

        with open(explorer_icon_dir, 'wb') as fo:
            fo.write(r.content)

    # Applies the dialog window icon
    root.iconbitmap(explorer_icon_dir)

def dep_download_ffmpeg() -> None:
    """
    Download the FFMPEG dependency
    :return: None
    """

    ffmpeg_exe = Path(f'{app_dir}/dependencies/ffmpeg.exe')

    if not ffmpeg_exe.is_file():
        print(f'\n{LWHITE}✏ FFMPEG is not installed, downloading...', end='\r')

        repo = 'https://github.com/GyanD/codexffmpeg/releases/latest'

        latest_ffmpeg = get(repo).url.rsplit('/', 1)[-1]
        build = f'ffmpeg-{latest_ffmpeg}-essentials_build'

        with RemoteZip(f'{repo}/download/{build}.zip') as rzip:
            total_size = rzip.getinfo(f'{build}/bin/ffmpeg.exe').compress_size

            rzip.extract(f'{build}/bin/ffmpeg.exe', Path(f'{app_dir}/dependencies'))
            Path(f'{app_dir}/dependencies/{build}/bin/ffmpeg.exe').rename(Path(f'{app_dir}/dependencies/ffmpeg.exe'))
            rmtree(Path(f'{app_dir}/dependencies/{build}'), ignore_errors=True)

            print(f'{LWHITE}✏ FFMPEG was successfully downloaded! (Compressed: {total_size / 1024 / 1024:.2f} MB & '
                  f'Uncompressed: {rzip.getinfo(f"{build}/bin/ffmpeg.exe").file_size / 1024 / 1024:.2f} MB)')

    environ['PATH'] += pathsep + path.join(getcwd(), Path(f'{app_dir}/dependencies'))

def format_string(string: str) -> str:
    """
    Format the string to be compatible with all operating systems
    :param string: required, string to be formatted
    :return: formatted string
    """

    # Format the string to be compatible with all operating systems
    new_string = str()
    allowed_chars = 'aáàâãbcçdeéèêfghiíìîjklmnoóòôõpqrstuúùûvwxyzAÁÀÂÃBCÇDEÉÈÊFGHIÍÌÎJKLMNOÓÒÔÕPQRSTUÚÙÛVWXYZ' \
                    '0123456789-_()[]{}# '

    for char in string:

        if char in allowed_chars:
            new_string += char

    new_string = sub(' +', ' ', new_string).strip()
    return new_string

def get_yt_thumbnail_url(url: str, resolution: str = 'maxresdefault', hostname: str = 'i.ytimg.com') -> str:
    """
    Return the thumbnail URL from a YouTube video
    :param url: required, any YouTube video url
    :param resolution: optional, thumbnail resolution
    :param hostname: optional, hostname of the thumbnail
    :return: thumbnail url
    """

    # url: any YouTube video url
    # resolution: 'maxresdefault', 'sddefault', 'hqdefault', 'mqdefault', 'default'
    # hostname: 'img.youtube.com' ou 'i.ytimg.com'

    # Returns the URL of the thumbnail of a YouTube video
    thumbnail_url = f'https://{hostname}/vi/{extract.video_id(url)}/{resolution}.jpg'
    return thumbnail_url

def enchance_music_file(yt, music_title: str) -> None:
    """
    Enchance the music file with the metadata, cover and re-encode it
    :param yt: required, youtube object
    :param music_title: required, music title
    :return: None
    """

    # Encoding the music file (by printing just one line of ffmpeg output in the terminal)
    makedirs(Path('songs'), exist_ok=True)

    input_music_dir = Path(f'{temp_dir}/songs/{music_title}.{ext}')
    output_music_dir = Path(f'songs/{music_title}.{ext}')

    subrun(f'ffmpeg -i "{input_music_dir}" -b:a 320k -vn "{output_music_dir}" -y -hide_banner -loglevel quiet -stats',
           shell=True)

    # Adds metadata to the music file
    publish_year = str(yt.publish_date).split('-')[0]

    f = tag_load_file(output_music_dir)
    f['artwork'] = open(Path(f'{temp_dir}/thumbnails/{music_title}.jpg'), 'rb').read()
    f['tracktitle'] = music_title
    f['artist'] = format_string(string=yt.author)
    f['year'] = publish_year
    f['albumartist'] = format_string(string=yt.author)
    f.save()

    # Delete the temporary music file and thumbnail
    remove(Path(f'{temp_dir}/songs/{music_title}.{ext}'))
    remove(Path(f'{temp_dir}/thumbnails/{music_title}.jpg'))

    print(f'{LWHITE}[{LGREEN}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] '
          f'{LGREEN}Music successfully saved!\n')

    app_env['success_downloads'] += 1

def download_music(url: str) -> None:
    """
    Download the music from the YouTube video and many other things
    :param url: required, any YouTube video url
    :return: None
    """

    total_attempts = 11
    retry_attempts = total_attempts
    retry_delay = 3

    while retry_attempts > 0:
        try:
            app_env['total_requests'] += 1
            retry_attempts -= 1

            yt = YouTube(url)
            music_title = format_string(string=yt.title)
            break

        except VideoRegionBlocked:
            print(f'{LWHITE}[{LRED}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] {LRED}'
                  f'Error when accessing the URL: {LBLUE}"{url}"{LRED}, because the song is {LBLUE}'
                  f'blocked in your region{LRED}! Jumping to the next in the list...\n')
            app_env['failed_downloads'] += 1
            return

        except AgeRestrictedError:
            print(f'{LWHITE}[{LRED}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] {LRED}'
                  f'Error when accessing the URL: {LBLUE}"{url}"{LRED}, as the song is {LBLUE}'
                  f'restricted to 18+ years old{LRED} and cannot be downloaded! Jumping to the next on the list...\n')
            app_env['failed_downloads'] += 1
            return

        except LiveStreamError:
            print(f'{LWHITE}[{LRED}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] {LRED}'
                  f'Error when accessing the URL: {LBLUE}"{url}"{LRED}, because the song is at {LBLUE}'
                  f'live{LRED} and it is not possible to download it! Jumping to the next in the list...\n')
            app_env['failed_downloads'] += 1
            return

        except VideoPrivate:
            print(f'{LWHITE}[{LRED}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] {LRED}'
                  f'Error when accessing the URL: {LBLUE}"{url}"{LRED}, because the song is {LBLUE}'
                  f'private{LRED} and cannot be accessed! Jumping to the next in the list...\n')
            app_env['failed_downloads'] += 1
            return

        except RecordingUnavailable:
            print(f'{LWHITE}[{LRED}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] {LRED}'
                  f'Error when accessing the URL: {LBLUE}"{url}"{LRED}, because the song is {LBLUE}'
                  f'indisavailable{LRED}! Jumping to the next in the list...\n')
            app_env['failed_downloads'] += 1
            return

        except MembersOnly:
            print(f'{LWHITE}[{LRED}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] {LRED}'
                  f'Error when accessing the URL: {LBLUE}"{url}"{LRED}, because the music is {LBLUE}'
                  f'exclusive to members{LRED} and cannot be downloaded! Jumping to the next on the list...\n')
            app_env['failed_downloads'] += 1
            return

        except VideoUnavailable:
            print(f'{LWHITE}[{LRED}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] {LRED}'
                  f'Error when accessing the URL: {LBLUE}"{url}"{LRED}, because the song is {LBLUE}'
                  f'indisavailable{LRED}! Jumping to the next in the list...\n')
            app_env['failed_downloads'] += 1
            return

        except Exception:
            if retry_attempts == 0:
                print(f'{LWHITE}[{LRED}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] {LRED}'
                      f'Jumping to the next on the list...\n')
                return

            else:
                print(f'{LWHITE}[{LRED}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] {LRED}'
                      f'Error on the {LBLUE}{total_attempts-retry_attempts}/{total_attempts-1}th {LRED}attempt! '
                      f'{LBLUE}Trying again...')

                sleep(retry_delay)

    # Get the URL of the thumbnail and saves it in a variable
    try:
        thumbnail_url = get_yt_thumbnail_url(url=url, resolution='maxresdefault', hostname='i.ytimg.com')

        # Download the song from YouTube
        if Path(Path(f'songs/{music_title}.{ext}')).is_file():
            print(f'{LWHITE}[{LYELLOW}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] '
                  f'{LYELLOW}Music {LBLUE}"{music_title}" {LYELLOW} has already been downloaded!\n')
            app_env['already_exists'] += 1
            return

        else:
            print(f'{LWHITE}[{LYELLOW}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] '
                  f'{LYELLOW}Downloading music {LBLUE}"{music_title}"{LYELLOW}...')

            makedirs(Path(f'{temp_dir}/songs'), exist_ok=True)

            yt_stream = yt.streams.filter(only_audio=True).get_audio_only()
            yt_stream.download(filename=f'{music_title}.{ext}', output_path=Path(f'{temp_dir}/songs'))

            # Download the thumbnail if the song has already been downloaded
            makedirs(Path(f'{temp_dir}/thumbnails'), exist_ok=True)

            r = get(thumbnail_url, allow_redirects=True)
            open(Path(f'{temp_dir}/thumbnails/{music_title}.jpg'), 'wb').write(r.content)

            enchance_music_file(yt, music_title=music_title)

    except Exception as e:
        print(f'{LWHITE}[{LRED}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] '
              f'{LRED}Error downloading music {LBLUE}"{music_title}"{LRED}! Error: {LBLUE}{e}\n')

def get_yt_url_from_query(query: str) -> str:
    """
    Searches the query on YouTube and returns the URL of the first result
    :param query: query to be searched on YouTube
    :return: url of the first result
    """

    # Searches the query on YouTube and returns the URL of the first result
    try:
        search = SearchVideos(query, offset=1, mode='dict', max_results=1)
        results = search.result()
        return results['search_result'][0]['link']

    except Exception as e:
        print(f'{LWHITE}[{LRED}{app_env["now_downloading"]}/{app_env["total_urls"]}{LWHITE}] '
              f'{LRED}Error when searching the song URL on YouTube! Error: {LBLUE}{e}\n')

def get_musics_from_youtube_playlist_url(url: str) -> list:
    """
    Returns a list of the songs in a YouTube playlist
    :param url: url of the YouTube playlist
    :return: list of the songs
    """

    urls = list(Playlist(f'https://www.youtube.com/playlist?list={extract.playlist_id(url)}').video_urls)
    return urls

def get_musics_from_resso_playlist_url(url: str) -> list:
    """
    Returns a list of the songs in a Resso playlist
    :param url: url of the Resso playlist
    :return: list of the songs
    """

    website_content = get(url).content
    music_tags = BeautifulSoup(
        website_content, 'html.parser').\
        find_all('img', src=lambda value: value.startswith('https://p16.resso.me/img/') and value.endswith('.jpg'))

    musics = [music['alt'] for music in music_tags[2:]]
    return musics

def get_musics_from_resso_track_url(url: str) -> str:
    """
    Returns the song in a Resso track
    :param url: url of the Resso track
    :return: song title
    """

    web_content = get(url).content
    music_title = BeautifulSoup(web_content, 'html.parser').find('title').text[:-30].replace('Official Resso', '\b')

    return music_title

def get_youtube_urls(query_list: list) -> list:
    """
    Returns a list of YouTube URLs from a list of queries
    :param query_list: list of queries
    :return: list of YouTube urls
    """

    regexes = {
        'youtube_playlist_url': r'^https?://(?:www\.|)youtu(?:\.be/|be\.com/(?:watch\?(?:.*&)?v=|embed/|v/)|\.com/'
                                r'(?:(?:m/)?user(?:/[^/]+)?|c/[^\s/]+))([\w-]{11})(?:\S+)?(?:\?|\&)list=([\w-]+)',
        'youtube_video_url': r'^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=[\w-]+(?![\w&=?+%-]*(?:list|playlist)'
                             r'[\w&=?+%-]*)',
        'resso_playlist_url': r'^(?:https?://)?(?:www\.)?resso\.com/playlist/\d+.*|(?:https?://)?m\.resso\.com/\w+.*$',
        'resso_track_url': r'https:\/\/www\.resso\.com\/track\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-_%?=&]+',
        'title': r'.*'
    }

    youtube_urls = list()
    for query in query_list:
        for source, regex in regexes.items():
            match = findall(regex, query)
            if match:
                if source == 'youtube_playlist_url':
                    new_urls = get_musics_from_youtube_playlist_url(url=query)
                    youtube_urls.extend(new_urls)

                elif source == 'youtube_video_url':
                    youtube_urls.append(query)

                elif source == 'resso_playlist_url':
                    names = get_musics_from_resso_playlist_url(url=query)
                    new_urls = get_youtube_urls(names)
                    youtube_urls.extend(new_urls)

                elif source == 'resso_track_url':
                    name = get_musics_from_resso_track_url(url=query)
                    new_url = get_yt_url_from_query(query=name)
                    youtube_urls.append(new_url)

                elif source == 'title':
                    new_url = get_yt_url_from_query(query=query)
                    youtube_urls.append(new_url)

                break

    return youtube_urls


# Check internet connection
if not is_internet_connected():
    input(f'{LWHITE}[{LRED}✖{LWHITE}] {LRED}Unstable internet connection! '
          f'{LYELLOW}Press ENTER or anything else to exit...')
    exit()

# Check if app is up to date
app_update_checker()

# Download the necessary files for the program to run
dep_download_assets()
dep_download_ffmpeg()

app_env = {
    'total_urls': 0,
    'now_downloading': 0,
    'success_downloads': 0,
    'already_exists': 0,
    'failed_downloads': 0,
    'total_requests': 0
}

def app():
    # Resets the app_env
    app_env['total_urls'] = 0
    app_env['now_downloading'] = 0
    app_env['success_downloads'] = 0
    app_env['already_exists'] = 0
    app_env['failed_downloads'] = 0
    app_env['total_requests'] = 0

    # Asks if the user wants to download the songs from a text file or write them manually
    print(f'\n{LWHITE}[{LYELLOW}?{LWHITE}] {LYELLOW}You can download the songs from a local {LCYAN}text file '
          f'{LYELLOW}or {LCYAN}write manually{LYELLOW}.\n')

    print(f'{LWHITE}[{LGREEN}!{LWHITE}] {LWHITE}To select a local text file, leave it blank and press ENTER.')
    print(f'{LWHITE}[{LGREEN}!{LWHITE}] {LWHITE}To type manually, type in some URL (from YouTube) or song name and '
          f'press ENTER.\n')

    print(f'{LWHITE}[{LRED}#{LWHITE}] {LRED}List of URLs/Queries - To choose a local text file, leave it blank and '
          f'press ENTER.')
    user_response = input(f'{LWHITE} ›{LBLUE} ')

    user_response = user_response.strip()
    if len(user_response) == 0:
        cl(jump_lines=1)

        print(f'{LWHITE}[{LYELLOW}!{LWHITE}] {LYELLOW}Opening the file explorer for you to select the local '
              f'text file...\n')

        # Opens a dialog window for selecting the input file
        input_file_path = filedialog.askopenfilename(title='Select a text file with the URLs/Queries',
                                                     filetypes=[('Text file', '*.txt'), ('All files', '*.*')])

        cl(jump_lines=1)

        # Opens the file in read-only mode, specifying the encoding as UTF-8
        start_time = time()

        with open(input_file_path.strip(), 'r', encoding='utf-8') as fi:
            query_list = [line.strip() for line in fi.readlines() if len(line.strip()) != 0]

    else:
        start_time = time()

        query_list = list()

        while len(user_response) != 0:
            query_list.append(user_response)
            user_response = input(f'{LWHITE} ›{LBLUE} ')

        app_env['total_urls'] = len(query_list)
        app_env['now_downloading'] = 0

        cl(jump_lines=1)

    youtube_urls = get_youtube_urls(query_list)
    app_env['total_urls'] = len(youtube_urls)

    app_env['now_downloading'] = 1
    for url in youtube_urls:
        download_music(url=url)
        app_env['now_downloading'] += 1

    # Deleting the temporary files folder
    rmtree(temp_dir, ignore_errors=True)

    print(f'{LWHITE}[{LGREEN}T{LWHITE}] {LGREEN}Runtime (total application execution time): '
          f'{LBLUE}{seconds_to_time(seconds=int(time() - start_time))}')
    print(f'{LWHITE}[{LGREEN}|{LWHITE}] {LGREEN}Saved (songs successfully downloaded and saved): '
          f'{LBLUE}{app_env["success_downloads"]}')
    print(f'{LWHITE}[{LGREEN}|{LWHITE}] {LGREEN}Ignored (songs that already existed in the output folder): '
          f'{LBLUE}{app_env["already_exists"]}')
    print(f'{LWHITE}[{LGREEN}L{LWHITE}] {LGREEN}Fails (songs not downloaded or unavailable): '
          f'{LBLUE}{app_env["failed_downloads"]}')


while True:
    app()
    key = input(f'\n{LWHITE}[{LYELLOW}!{LWHITE}] {LYELLOW}Press ENTER to continue or anything else to exit...')

    if key != '':
        break

    cl(jump_lines=1)
