from PIL import Image  # type: ignore
from datetime import datetime
from os import getcwd, environ
from pathlib import Path
from sys import exit
from time import sleep

from py_functions import (
    app_utils,
    music_platforms as mup,
)


# Application settings
class AppConfig:
    VERSION = '1.1.2'
    GITHUB_REPOSITORY = 'https://github.com/Henrique-Coder/batch-music-downloader'
    NAME = 'Batch Music Downloader'
    PATH = getcwd(), NAME.replace(' ', '')
    ENV_PATH = Path(*PATH, 'assets/pathenv')
    OUTPUT_PATH = Path('songs')


# Initializing Colorama and terminal functions
app_utils.clsr(1)
app_utils.init_colorama(autoreset=True)
TColor = app_utils.TerminalTextColors
TBracket = app_utils.TerminalCustomBrackets

# Checking internet connection
if not app_utils.is_internet_connected('https://www.google.com', 5):
    input(
        f'{TBracket(TColor.LRED, "ERROR")} {TColor.RED}Very slow or non-existent internet connection - '
        f'Press ENTER to exit...'
    )
    exit()

# Checking if app is updated
is_updated, latest_version_available, lastest_release_url = app_utils.is_app_updated(
    AppConfig.VERSION, AppConfig.GITHUB_REPOSITORY
)
if not is_updated:
    print(
        f'{TBracket(TColor.LYELLOW, "WARN")} {TColor.YELLOW}This app version is out of date, '
        f'the latest available version is {TColor.GREEN}{latest_version_available}'
        f'\n{TBracket(TColor.LYELLOW, "WARN")} {TColor.YELLOW}Download it at: '
        f'{TColor.BLUE}{lastest_release_url}\n'
    )

# Creating app folders
app_folder = Path(*AppConfig.PATH)
app_utils.create_dirs(app_folder, ['assets/media', 'assets/pathenv'])

# Checking if app assets exists and downloading if not
path_explorer_file_dialog_ico = Path(app_folder, 'assets/media/ExplorerFileDialog.ico')
if not path_explorer_file_dialog_ico.exists():
    base64_explorer_file_dialog_ico = 'AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAgBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///wT///9R////kv///6r///+k////cf///yAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8d////0////////////////////////////////f///5f///8KAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///8b//////////////////////////////////////////////8r///8LAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8f/////////////////////////////////////////////////////////5YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///yf/////////////////////////////////////////////////////////+f///xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8e////lP///9b////u////6P///8H///92////DwAAAAAAAAAAAAAAAAAAAAAAAAAA////Bf///+r/////////////////////////////////////////////////////////PwAAAAAAAAAAAAAAAAAAAAAAAAAA////OP///+7////////////////////////////////////n////SAAAAAAAAAAAAAAAAAAAAAAAAAAA////c/////////////////////////////////////////////////////////9KAAAAAAAAAAAAAAAAAAAAAP///wL////c///////////////////////////////////////////////8////TAAAAAAAAAAAAAAAAAAAAAD///8C////pf///////////////////////////////////////////////////0oAAAAAAAAAAAAAAAAAAAAA////JP/////////////////////////////////////////////////////////q////DgAAAAAAAAAAAAAAAAAAAAD///8C////ef////L/////////////////////////////////////////SgAAAAAAAAAAAAAAAAAAAAD///8i//////////////////////////////////////////////////////////////9dAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////EP///2r///+o////u////7T///+O//////////////9KAAAAAAAAAAAAAAAAAAAAAP///wH////b/////////////////////////////////////////////////////////4UAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///yL//////////////0oAAAAAAAAAAAAAAAAAAAAAAAAAAP///1H////+////////////////////////////////////////////////////iQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////Iv//////////////SgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///3L////8//////////////////////////////////////////////+JAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8i//////////////9KAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///zn///++/////////////////////////////////////////4kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///yL//////////////0oAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8l////Vv///2b///9b////Jf///+T/////////iQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////Iv//////////////SgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////5P////////+JAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8i//////////////9KAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD////k/////////4kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///yL//////////////0oAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///+T/////////iQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////Iv//////////////SgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////5P////////+JAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8i//////////////9kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD////k/////////4kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///yL//////////////+f///9I////AgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///+T/////////iQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////Iv/////////////////////////Z////iP///zz///8CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////5P////////+JAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8i/////////////////////////////////////////+f///+R////RP///wgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD////k/////////4kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///yL/////////////////////////////////////////////////////////+P///7X///9l////FgAAAAAAAAAAAAAAAP///+X/////////iQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////If/////////////////////////////////////////////////////////////////////////9////w////3T///9m/////v////////+JAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8F////+P///////////////////////////////////////////////////////////////////////////////////////////////////4kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///+e////////////////////////////////////////////////////////////////////////////////////////////////////iQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///xD////J//////////////////////////////////////////////////////////////////////////////////////////////+JAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///wn///9y////0////////////////////////////////////////////////////////////////////////////////////4kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////M////4D////M/////f//////////////////////////////////////////////////////////////iQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///8P////Vv///6P////t//////////////////////////////////////////////+GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///wP///8/////i////9n//////////////////////////////1YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///yb///90////vP///9n///+G////AQAAAAAAAAAA8f///8A///+AH///gA///4AP8H+AD+AfwA/AD8APwAfwD8AH/A/AA//P4AP/z/AD/8/4A//P/+P/z//j/8//4//P/+P/z//j/8//4//H/+P/wP/j/8Af4//AA+P/wABj/8AAA//AAAP/4AAD//gAA//+AAP//+AD///8B////8c='
    app_utils.base64_decoder(
        base64_data=base64_explorer_file_dialog_ico,
        output_file_path=path_explorer_file_dialog_ico
    )

ffmpeg_path = Path(AppConfig.ENV_PATH / 'ffmpeg.exe')
if not ffmpeg_path.exists():
    start_time = datetime.now().strftime('%H:%M:%S:%f')
    print(
        f'{TBracket(TColor.LYELLOW, "WARN")} {TColor.YELLOW}FFMPEG auto-download started at {start_time}', end='\r'
    )

    # Downloading ffmpeg
    app_utils.download_latest_ffmpeg(AppConfig.ENV_PATH, 'ffmpeg')

    # Set environment path
    environ['PATH'] += f';{AppConfig.ENV_PATH}'

    print(
        f'{TBracket(TColor.LGREEN, "SUCCESS")} {TColor.GREEN}FFMPEG auto-download started at {TColor.YELLOW}{start_time} '
        f'{TColor.GREEN}and ended successfully at {TColor.YELLOW}{datetime.now().strftime("%H:%M:%S:%f")}{TColor.GREEN}.\n'
    )

# Creating main query variables
class AppQueries:
    queries_file_path = None
    query_list = list()

# Creating downloading status variables
class AppStats:
    total_urls = int()
    current_downloading = int()
    successful_downloads = int()
    existing_files = int()
    failed_downloads = int()
    total_requests = int()

# Creating service URLs
class MusicServiceURLs:
    all_urls = list()
    youtube_playlist = list()
    youtube_track = list()
    resso_playlist = list()
    resso_track = list()

def app():
    def reseting_variables() -> None:
        """
        Resetting some variables
        :return:  None
        """

        # Resetting main query variables
        AppQueries.queries_file_path = None
        AppQueries.query_list = list()

        # Resetting downloading status variables
        AppStats.total_urls = 0
        AppStats.current_downloading = 0
        AppStats.successful_downloads = 0
        AppStats.existing_files = 0
        AppStats.failed_downloads = 0

        # Resetting service URLs
        MusicServiceURLs.all_urls = list()
        MusicServiceURLs.youtube_playlist = list()
        MusicServiceURLs.youtube_track = list()
        MusicServiceURLs.resso_playlist = list()
        MusicServiceURLs.resso_track = list()
    reseting_variables()

    # Asks if the user wants to download the songs from a text file or write manually
    print(
        f'{TBracket(TColor.LYELLOW, "+")} {TColor.YELLOW}You can download the songs from a local {TColor.CYAN}text file '
        f'{TColor.YELLOW}or {TColor.CYAN}write manually{TColor.YELLOW}.\n\n'
        f'{TBracket(TColor.LWHITE, "-")} {TColor.WHITE}To select a local text file, leave it blank and press ENTER.\n'
        f'{TBracket(TColor.LWHITE, "-")} {TColor.WHITE}To type manually, type in some URL (from available services) or song name and press ENTER.\n\n'
        f'{TBracket(TColor.LRED, "#")} {TColor.RED}List of URLs/Queries must be separated by a new line, if last line is empty, program will start downloading.'
    )

    user_response = input(f'{TColor.LWHITE} ›{TColor.BLUE} ')
    if not len(user_response.strip()):
        # If the user has not typed anything, open the file explorer for him to select the file
        app_utils.clsr(1)
        print(
            f'{TBracket(TColor.LYELLOW, "+")} {TColor.YELLOW}Opening the file explorer for you to select the local '
            f'text file...'
        )

        queries_file_path = app_utils.filedialog_selector(
            window_title='Select a text file with the URLs/Queries',
            window_icon_path=path_explorer_file_dialog_ico,
            allowed_file_types=[('Text files', '*.txt'), ('All files', '*.*')]
        )

        # If the user has not selected any file, finish the program
        if not queries_file_path:
            print(
                f'{TBracket(TColor.LRED, "ERROR")} {TColor.RED}You have not selected any file, exiting...'
            )
            return

        # If the user has selected a file, read it and store the queries in a list
        with open(queries_file_path, 'r', encoding='utf-8') as fi:
            AppQueries.query_list = [
                line.strip() for line in fi.readlines() if len(line.strip()) != 0
            ]

        AppStats.total_urls = len(AppQueries.query_list)

    else:
        # If the user has typed something, store the queries in a list
        while len(user_response) != 0:
            AppQueries.query_list.append(user_response)
            user_response = input(f'{TColor.LWHITE} ›{TColor.BLUE} ')

        AppStats.total_urls = len(AppQueries.query_list)

    # Clear the screen
    app_utils.clsr(1)

    # Separa as URLs/Queries por serviço
    print(
        f'{TBracket(TColor.LBLUE, "RUNNING")} {TColor.BLUE}Separating URLs/Queries by service...'
    )
    mup.music_platform_categorizer(MusicServiceURLs, AppQueries.query_list, TColor)
    print(
        f'  {TColor.LWHITE}YouTube (Track): {TColor.GREEN}{len(MusicServiceURLs.youtube_track)}\n'
        f'  {TColor.LWHITE}YouTube (Playlist): {TColor.GREEN}{len(MusicServiceURLs.youtube_playlist)}\n'
        f'  {TColor.LWHITE}Resso (Track): {TColor.GREEN}{len(MusicServiceURLs.resso_track)}\n'
        f'  {TColor.LWHITE}Resso (Playlist): {TColor.GREEN}{len(MusicServiceURLs.resso_playlist)}\n'
        f'  {TColor.LGREEN}Total of {len(MusicServiceURLs.youtube_track + MusicServiceURLs.youtube_playlist + MusicServiceURLs.resso_track + MusicServiceURLs.resso_playlist)} items'
    )

    # Get YouTube URLs
    print(
        f'{TBracket(TColor.LBLUE, "RUNNING", 1)} {TColor.BLUE}Converting into YouTube URLs...'
    )

    queries = list()

    for playlist_url in MusicServiceURLs.youtube_playlist:
        songs = mup.get_musics_from_youtube_playlist(playlist_url)
        queries.extend(songs)

    MusicServiceURLs.all_urls.extend(queries)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(queries)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.youtube_playlist)}{TColor.WHITE} YouTube playlist(s)'
    )

    MusicServiceURLs.all_urls.extend(MusicServiceURLs.youtube_track)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(MusicServiceURLs.youtube_track)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.youtube_track)}{TColor.WHITE} YouTube track(s)'
    )

    queries = [mup.get_youtube_url_from_query(music_name)
               for playlist_url in MusicServiceURLs.resso_playlist
               for music_name in mup.get_music_name_from_resso_playlist(playlist_url)]
    MusicServiceURLs.all_urls.extend(queries)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(queries)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.resso_playlist)}{TColor.WHITE} Resso playlist(s)'
    )

    queries = [mup.get_youtube_url_from_query(mup.get_music_name_from_resso_track(music_url))
               for music_url in MusicServiceURLs.resso_track]
    MusicServiceURLs.all_urls.extend(queries)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(queries)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.resso_track)}{TColor.WHITE} Resso track(s)'
    )

    print(
        f'  {TColor.LGREEN}Total of {len(MusicServiceURLs.all_urls)} YouTube URL(s)'
    )

    # Fixing URLs list
    for url in MusicServiceURLs.all_urls:
        if url is None:  # If the URL is None, remove it from the list
            MusicServiceURLs.all_urls.remove(url)
        elif url == str():  # If the URL is empty, remove it from the list
            MusicServiceURLs.all_urls.remove(url)
        elif MusicServiceURLs.all_urls.count(url) > 1:  # If the URL is duplicated, remove it from the list
            MusicServiceURLs.all_urls.remove(url)

    # Downloading the songs
    print()
    for url in MusicServiceURLs.all_urls:
        now_downloading = MusicServiceURLs.all_urls.index(url) + 1

        print(
            f"{TBracket(TColor.LBLUE, 'RUNNING')} {TColor.BLUE}Downloading: {url} - {TColor.LWHITE}[{TColor.BLUE}{now_downloading}{TColor.LWHITE}/{TColor.BLUE}{len(MusicServiceURLs.all_urls)}{TColor.LWHITE}]"
        )
        info = mup.get_youtube_song_metadata(url)
        music_path = mup.download_song_from_youtube(info, AppConfig.OUTPUT_PATH)
        mup.add_song_metadata(info, music_path)

    # Finishing the program
    print(
        f'\n{TBracket(TColor.LGREEN, "SUCCESS")} {TColor.GREEN}All songs downloaded successfully!'
    )


while True:
    app()
    key = input(
        f'{TBracket(TColor.LWHITE, "END", 1)} {TColor.WHITE}Press ENTER to continue or anything else to exit...'
    )
    if key != str():
        break

    app_utils.clsr(1)
