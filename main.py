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
from requests import get
from tqdm import tqdm
from youtubesearchpython import SearchVideos
from zstd import ZSTD_uncompress


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

# Creating initial variables
ext = 'mp3'
success_downloads = 0
already_exists = 0
failed_downloads = 0
total_requests = 0

# Creating variables for the program directory
app_name = 'Batch Music Downloader [by Henrique-Coder]'
app_dir = Path(environ['userprofile'] + fr'\AppData\Local\{app_name}')
temp_dir = Path(fr'{app_dir}\.temp')

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

def tqdm_custom_bar(current, total, width=40, char='') -> str:
    """
    TQDM dependency for the custom progress bar
    """

    filled_length = int(width * current / total)
    empty_length = width - filled_length
    bar = char * filled_length + ' ' * empty_length

    return f'[{bar}]'

def dep_download_assets() -> None:
    """
    Download the application assets (tiny things)
    :return: None
    """

    # Creates the application directory if it doesn't exist
    makedirs(fr'{app_dir}\dependencies', exist_ok=True)

    # Starts the Tkinter window and hides it
    root = Tk()
    root.withdraw()

    # Download the application favicon
    favicon_url = 'https://raw.githubusercontent.com/Henrique-Coder/batch-music-downloader/main/favicon.ico'
    favicon_dir = fr'{app_dir}\favicon.ico'

    if not Path(favicon_dir).is_file():
        r = get(favicon_url, allow_redirects=True)

        with open(favicon_dir, 'wb') as fo:
            fo.write(r.content)

    # Download the dialog window icon if it doesn't exist
    makedirs(fr'{app_dir}\assets', exist_ok=True)

    explorer_ico_url = 'https://raw.githubusercontent.com/Henrique-Coder/batch-music-downloader/main/online_assets/explorer.ico'
    explorer_ico_dir = fr'{app_dir}\assets\explorer.ico'

    if not Path(explorer_ico_dir).is_file():
        r = get(explorer_ico_url, allow_redirects=True)

        with open(explorer_ico_dir, 'wb') as fo:
            fo.write(r.content)

    # Applies the dialog window icon
    root.iconbitmap(explorer_ico_dir)

def dep_download_ffmpeg() -> None:
    """
    Download the FFMPEG executable and unpack it with ZSTD and then set it as an environment variable
    :return: None
    """

    # Downloading the FFMPEG compressed [Size: ~41MB]
    ffmpeg_exe_zst = Path(fr'{app_dir}\dependencies\ffmpeg.exe.zst')
    ffmpeg_exe = Path(fr'{app_dir}\dependencies\ffmpeg.exe')

    if not ffmpeg_exe.is_file():
        ffmpeg_url = 'https://drive.google.com/uc?export=download&id=16Ob9qv7uwLWqcMOwTOKeC9p52accn-wO'

        r = get(ffmpeg_url, allow_redirects=True, stream=True)
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024

        # Configure the progress bar format and animation
        print(f'{LWHITE}[{LRED}!{LWHITE}] {LRED}FFMPEG was not found in the default location! So it will be downloaded automatically...')
        bar_format = '★ Progress › {bar} ‹ {percentage:3.1f}% • Rate|Downloaded|Total: {rate_fmt}{postfix}|{n_fmt}|{total_fmt} — Elapsed|Remaining: {elapsed}|{remaining}'
        anim_rotation_dot = ' ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏━'

        with open(ffmpeg_exe_zst, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True, dynamic_ncols=True,
                                                   bar_format=bar_format, ascii=anim_rotation_dot,
                                                   mininterval=0.1, smoothing=True) as pbar:

            for data in r.iter_content(block_size):
                f.write(data)
                pbar.set_description(tqdm_custom_bar(pbar.n, total_size))
                pbar.update(len(data))

        # Unpacking FFMPEG with ZSTD [Size unpacked: ~123MB]
        with open(fr'{app_dir}\dependencies\ffmpeg.exe.zst', mode='rb') as fi:
            with open(fr'{app_dir}\dependencies\ffmpeg.exe', mode='wb') as fo:
                fo.write(ZSTD_uncompress(fi.read()))

        # Deleting the compressed FFMPEG file
        remove(fr'{app_dir}\dependencies\ffmpeg.exe.zst')
    environ['PATH'] += pathsep + path.join(getcwd(), fr'{app_dir}\dependencies')

def format_string(string: str) -> str:
    """
    Format the string to be compatible with all operating systems
    :param string: required, string to be formatted
    :return: formatted string
    """

    # Format the string to be compatible with all operating systems
    new_string = ''
    for char in string:
        if char in 'aáàâãbcçdeéèêfghiíìîjklmnoóòôõpqrstuúùûvwxyzAÁÀÂÃBCÇDEÉÈÊFGHIÍÌÎJKLMNOÓÒÔÕPQRSTUÚÙÛVWXYZ0123456789-_()[]{}# ':
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

    # Globalize the variables
    global success_downloads

    # Encoding the music file (by printing just one line of ffmpeg output in the terminal)
    makedirs('songs', exist_ok=True)

    subrun(fr'ffmpeg -i "{temp_dir}\songs\{music_title}.{ext}" -b:a 320k -vn "songs\{music_title}.{ext}" -y -hide_banner -loglevel quiet -stats', shell=True)

    # Adds metadata to the music file
    publish_year = str(yt.publish_date).split('-')[0]

    f = tag_load_file(fr'songs\{music_title}.{ext}')
    f['artwork'] = open(fr'{temp_dir}\thumbnails\{music_title}.jpg', 'rb').read()
    f['tracktitle'] = music_title
    f['artist'] = format_string(string=yt.author)
    f['year'] = publish_year
    f['albumartist'] = format_string(string=yt.author)
    f.save()

    # Delete the temporary music file and thumbnail
    remove(fr'{temp_dir}\songs\{music_title}.{ext}')
    remove(fr'{temp_dir}\thumbnails\{music_title}.jpg')

    print(f'{LWHITE}[{LGREEN}{now_downloading}/{total_urls}{LWHITE}] {LGREEN}Music successfully saved!\n')

    success_downloads += 1

def download_music(url: str, now_downloading: int, total_urls: int) -> None:
    """
    Download the music from the YouTube video and many other things
    :param url: required, any YouTube video url
    :param now_downloading: required, the current download number
    :param total_urls: required, the total of urls in the list
    :return: None
    """

    # Globalize the variables
    global already_exists, failed_downloads, total_requests

    total_attempts = 16
    retry_attempts = total_attempts
    retry_delay = 3

    while retry_attempts > 0:
        try:
            total_requests += 1
            retry_attempts -= 1

            yt = YouTube(url)
            music_title = format_string(string=yt.title)
            break

        except VideoRegionBlocked:
            print(f'{LWHITE}[{LRED}{now_downloading}/{total_urls}{LWHITE}] {LRED}Error when accessing the URL: {LBLUE}"{url}"{LRED}, because the song is {LBLUE}blocked in your region{LRED}! Jumping to the next in the list...\n')
            failed_downloads += 1
            return
        except AgeRestrictedError:
            print(f'{LWHITE}[{LRED}{now_downloading}/{total_urls}{LWHITE}] {LRED}Error when accessing the URL: {LBLUE}"{url}"{LRED}, as the song is {LBLUE}restricted to 18+ years old{LRED} and cannot be downloaded anonymously! Jumping to the next on the list...\n')
            failed_downloads += 1
            return
        except LiveStreamError:
            print(f'{LWHITE}[{LRED}{now_downloading}/{total_urls}{LWHITE}] {LRED}Error when accessing the URL: {LBLUE}"{url}"{LRED}, because the song is at {LBLUE}live{LRED} and it is not possible to download it! Jumping to the next in the list...\n')
            failed_downloads += 1
            return
        except VideoPrivate:
            print(f'{LWHITE}[{LRED}{now_downloading}/{total_urls}{LWHITE}] {LRED}Error when accessing the URL: {LBLUE}"{url}"{LRED}, because the song is {LBLUE}private{LRED} and cannot be accessed! Jumping to the next in the list...\n')
            failed_downloads += 1
            return
        except RecordingUnavailable:
            print(f'{LWHITE}[{LRED}{now_downloading}/{total_urls}{LWHITE}] {LRED}Error when accessing the URL: {LBLUE}"{url}"{LRED}, because the song is {LBLUE}indisavailable{LRED}! Jumping to the next in the list...\n')
            failed_downloads += 1
            return
        except MembersOnly:
            print(f'{LWHITE}[{LRED}{now_downloading}/{total_urls}{LWHITE}] {LRED}Error when accessing the URL: {LBLUE}"{url}"{LRED}, because the music is {LBLUE}exclusive to members{LRED} and cannot be downloaded anonymously! Jumping to the next on the list...\n')
            failed_downloads += 1
            return
        except VideoUnavailable:
            print(f'{LWHITE}[{LRED}{now_downloading}/{total_urls}{LWHITE}] {LRED}Error when accessing the URL: {LBLUE}"{url}"{LRED}, because the song is {LBLUE}indisavailable{LRED}! Jumping to the next in the list...\n')
            failed_downloads += 1
            return

        except Exception as e:
            if retry_attempts == 0:
                print(f'{LWHITE}[{LRED}{now_downloading}/{total_urls}{LWHITE}] {LRED}Jumping to the next on the list...\n')
                return

            else:
                print(f'{LWHITE}[{LRED}{now_downloading}/{total_urls}{LWHITE}] {LRED}Error on the {LBLUE}{total_attempts-retry_attempts}/{total_attempts-1}th {LRED}attempt: {LBLUE}"{e}"{LRED}! Trying again...')
                sleep(retry_delay)

    # Get the URL of the thumbnail and saves it in a variable
    try:
        thumbnail_url = get_yt_thumbnail_url(url=url, resolution='maxresdefault', hostname='i.ytimg.com')

        # Download the song from YouTube
        if Path(fr'songs\{music_title}.{ext}').is_file():
            print(f'{LWHITE}[{LYELLOW}{now_downloading}/{total_urls}{LWHITE}] {LYELLOW}Music {LBLUE}"{music_title}" {LYELLOW} has already been downloaded!\n')
            already_exists += 1
            return

        else:
            print(f'{LWHITE}[{LYELLOW}{now_downloading}/{total_urls}{LWHITE}] {LYELLOW}Downloading music {LBLUE}"{music_title}"{LYELLOW}...')

            makedirs(fr'{temp_dir}\songs', exist_ok=True)

            yt_stream = yt.streams.filter(only_audio=True).get_audio_only()
            yt_stream.download(filename=f'{music_title}.{ext}', output_path=f'{temp_dir}\songs')

            # Download the thumbnail if the song has already been downloaded
            makedirs(fr'{temp_dir}\thumbnails', exist_ok=True)

            r = get(thumbnail_url, allow_redirects=True)
            open(fr'{temp_dir}\thumbnails\{music_title}.jpg', 'wb').write(r.content)

            enchance_music_file(yt, music_title=music_title)

    except Exception as e:
        print(f'{LWHITE}[{LRED}{now_downloading}/{total_urls}{LWHITE}] {LRED}Error downloading music {LBLUE}"{music_title}"{LRED}! Error: {LBLUE}{e}\n')

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
        return str(results['search_result'][0]['link'])

    except Exception as e:
        print(f'{LWHITE}[{LRED}{now_downloading}/{total_urls}{LWHITE}] {LRED}Error when searching the song URL on YouTube! Error: {LBLUE}{e}\n')

def get_musics_from_youtube_playlist_url(url: str) -> list:
    """
    Returns a list of the songs in a YouTube playlist
    :param url: url of the YouTube playlist
    :return: list of the songs
    """

    playlist_id = extract.playlist_id(url)
    playlist_url = f'https://www.youtube.com/playlist?list={playlist_id}'

    playlist = Playlist(playlist_url)
    urls = list(playlist.video_urls)

    return urls

def get_musics_from_resso_playlist_url(url: str) -> list:
    """
    Returns a list of the songs in a Resso playlist
    :param url: url of the Resso playlist
    :return: list of the songs
    """

    website = get(url).content
    music_tags = BeautifulSoup(website, 'html.parser').find_all('img', src=lambda value: value.startswith('https://p16.resso.me/img/') and value.endswith('.jpg'))
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
        'youtube_playlist_url': r'^https?://(?:www\.|)youtu(?:\.be/|be\.com/(?:watch\?(?:.*&)?v=|embed/|v/)|\.com/(?:(?:m/)?user(?:/[^/]+)?|c/[^\s/]+))([\w-]{11})(?:\S+)?(?:\?|\&)list=([\w-]+)',
        'youtube_video_url': r'^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=[\w-]+(?![\w&=?+%-]*(?:list|playlist)[\w&=?+%-]*)',
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


# Download the necessary files for the program to run
dep_download_assets()
dep_download_ffmpeg()

# Asks if the user wants to download the songs from a text file or write them manually
print(f'\n{LWHITE}[{LYELLOW}?{LWHITE}] {LYELLOW}You can download the songs from a local {LCYAN}text file {LYELLOW}or {LCYAN}write manually{LYELLOW}.\n')

print(f'{LWHITE}[{LGREEN}!{LWHITE}] {LWHITE}To select a local text file, leave it blank and press ENTER.')
print(f'{LWHITE}[{LGREEN}!{LWHITE}] {LWHITE}To type manually, type in some URL (from YouTube) or song name and press ENTER.\n')

print(f'{LWHITE}[{LRED}#{LWHITE}] {LRED}List of URLs/Queries - To choose a local text file, leave it blank and press ENTER.')
user_response = input(f'{LWHITE} ›{LBLUE} ')

user_response = user_response.strip()
if len(user_response) == 0:
    cl(jump_lines=1)

    print(f'{LWHITE}[{LYELLOW}!{LWHITE}] {LYELLOW}Opening the file explorer for you to select the local text file...\n')

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

    total_urls = len(query_list)
    now_downloading = 0

    cl(jump_lines=1)

youtube_urls = get_youtube_urls(query_list)
total_urls = len(youtube_urls)

now_downloading = 1
for url in youtube_urls:
    download_music(url=url, now_downloading=now_downloading, total_urls=total_urls)
    now_downloading += 1

# Deletando a pasta de arquivos temporarios
rmtree(temp_dir, ignore_errors=True)

print(f'{LWHITE}[{LGREEN}T{LWHITE}] {LGREEN}Runtime: {LBLUE}{seconds_to_time(seconds=int(time() - start_time))}')
print(f'{LWHITE}[{LGREEN}|{LWHITE}] {LGREEN}Saved: {LBLUE}{success_downloads}')
print(f'{LWHITE}[{LGREEN}|{LWHITE}] {LGREEN}Ignored (they already existed): {LBLUE}{already_exists}')
print(f'{LWHITE}[{LGREEN}L{LWHITE}] {LGREEN}Fails: {LBLUE}{failed_downloads}')

input(f'\n{LWHITE}[{LYELLOW}!{LWHITE}] {LYELLOW}Press ENTER to exit...')
