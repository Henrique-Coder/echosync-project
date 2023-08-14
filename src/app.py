from datetime import datetime
from os import getcwd, environ
from pathlib import Path

from app_functions import (
    base64_items,
    app_utils,
    music_platforms as mup,
)


# Application settings
class AppConfig:
    VERSION = '1.1.4'
    GITHUB_REPOSITORY = 'https://github.com/Henrique-Coder/echosync-project'
    NAME = 'EchoSync Project'
    PATH = Path(getcwd(), NAME)
    CONFIG_PATH = Path(PATH, '.config')
    ENV_PATH = Path(CONFIG_PATH, 'pathenv')
    OUTPUT_PATH = Path(PATH, 'output/musics')


# Initializing Colorama and terminal functions
app_utils.clsr(1)
app_utils.init_colorama(autoreset=True)
TColor = app_utils.TerminalTextColors
TBracket = app_utils.TerminalCustomBrackets

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
config_folder = AppConfig.CONFIG_PATH
app_utils.create_dirs(config_folder, ['pathenv', 'media/icons'])
app_utils.hide_windows_folder(config_folder)

# Checking if app assets exists and downloading if not
path_explorer_file_dialog_ico = Path(config_folder, 'media/icons/ExplorerFileDialog.ico')
if not path_explorer_file_dialog_ico.exists():
    base64_explorer_file_dialog_ico = base64_items.base64_explorer_file_dialog_ico
    app_utils.base64_decoder(
        base64_data=base64_explorer_file_dialog_ico,
        output_file_path=path_explorer_file_dialog_ico,
    )

# Checking if ffmpeg exists and downloading if not
ffmpeg_path = Path(AppConfig.ENV_PATH / 'ffmpeg.exe')
if not ffmpeg_path.exists():
    start_time = datetime.now().strftime('%Hh%Mm%Ss')
    print(
        f'{TBracket(TColor.LYELLOW, "WARN")} {TColor.YELLOW}FFMPEG auto-download started at {start_time}',
        end='\r',
    )

    # Downloading ffmpeg
    app_utils.download_latest_ffmpeg(AppConfig.ENV_PATH, 'ffmpeg')

    # Set environment path
    environ['PATH'] += f';{AppConfig.ENV_PATH}'

    print(
        f'{TBracket(TColor.LGREEN, "SUCCESS")} {TColor.GREEN}FFMPEG auto-download started at {TColor.YELLOW}{start_time} '
        f'{TColor.GREEN}and ended successfully at {TColor.YELLOW}{datetime.now().strftime("%Hh%Mm%Ss")}{TColor.GREEN}.\n'
    )


# Creating main query variables
class AppQueries:
    queries_file_path = None
    query_list = list()


# Creating downloading status variables
class AppStats:
    total_urls = int()


# Creating service URLs
class MusicServiceURLs:
    all_urls = list()
    youtube_playlist = list()
    youtube_track = list()
    resso_playlist = list()
    resso_track = list()
    deezer_playlist = list()
    deezer_track = list()
    spotify_playlist = list()
    spotify_track = list()
    tiktokmusic_playlist = list()
    tiktokmusic_track = list()


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

        # Resetting service URLs
        MusicServiceURLs.all_urls = list()
        MusicServiceURLs.youtube_playlist = list()
        MusicServiceURLs.youtube_track = list()
        MusicServiceURLs.resso_playlist = list()
        MusicServiceURLs.resso_track = list()
        MusicServiceURLs.deezer_playlist = list()
        MusicServiceURLs.deezer_track = list()
        MusicServiceURLs.spotify_playlist = list()
        MusicServiceURLs.spotify_track = list()
        MusicServiceURLs.tiktokmusic_playlist = list()
        MusicServiceURLs.tiktokmusic_track = list()

    reseting_variables()

    # Asks if the user wants to download the songs from a text file or write manually
    print(
        f'{TBracket(TColor.LYELLOW, "+")} {TColor.YELLOW}You can download the songs from a local {TColor.CYAN}text file '
        f'{TColor.YELLOW}or {TColor.CYAN}write manually{TColor.YELLOW}.\n\n'
        f'{TBracket(TColor.LWHITE, "-")} {TColor.WHITE}To select a local text file, leave it blank and press ENTER.\n'
        f'{TBracket(TColor.LWHITE, "-")} {TColor.WHITE}To type manually, type in some URL (from available services) or song name and press ENTER.\n\n'
        f'{TBracket(TColor.LRED, "#")} {TColor.RED}List of URLs/Queries must be separated by a new line, if last line is empty, program will start downloading.'
    )

    user_response = app_utils.unshorten_url(input(f'{TColor.LWHITE} ›{TColor.BLUE} '), remove_url_params=True)
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
            allowed_file_types=[('Text files', '*.txt')],
        )

        # If the user has not selected any file, finish the program
        if not queries_file_path:
            print(
                f'{TBracket(TColor.LRED, "ERROR")} {TColor.RED}You have not selected any file, restarting the program...'
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
            user_response = app_utils.unshorten_url(input(f'{TColor.LWHITE} ›{TColor.BLUE} '), remove_url_params=True)
        AppStats.total_urls = len(AppQueries.query_list)

    # Clear the screen
    app_utils.clsr(1)

    # Separate URLs/Queries by service
    print(
        f'{TBracket(TColor.LBLUE, "RUNNING")} {TColor.BLUE}Separating URLs/Queries by service...'
    )
    mup.music_platform_categorizer(MusicServiceURLs, AppQueries.query_list, TColor)
    print(
        f'  {TColor.LWHITE}YouTube (Playlist): {TColor.GREEN}{len(MusicServiceURLs.youtube_playlist)}\n'
        f'  {TColor.LWHITE}YouTube (Track): {TColor.GREEN}{len(MusicServiceURLs.youtube_track)}\n'
        f'  {TColor.LWHITE}Resso (Playlist): {TColor.GREEN}{len(MusicServiceURLs.resso_playlist)}\n'
        f'  {TColor.LWHITE}Resso (Track): {TColor.GREEN}{len(MusicServiceURLs.resso_track)}\n'
        f'  {TColor.LWHITE}Deezer (Playlist): {TColor.GREEN}{len(MusicServiceURLs.deezer_playlist)}\n'
        f'  {TColor.LWHITE}Deezer (Track): {TColor.GREEN}{len(MusicServiceURLs.deezer_track)}\n'
        f'  {TColor.LWHITE}Spotify (Playlist): {TColor.GREEN}{len(MusicServiceURLs.spotify_playlist)}\n'
        f'  {TColor.LWHITE}Spotify (Track): {TColor.GREEN}{len(MusicServiceURLs.spotify_track)}\n'
        f'  {TColor.LWHITE}TikTok Music (Playlist): {TColor.GREEN}{len(MusicServiceURLs.tiktokmusic_playlist)}\n'
        f'  {TColor.LWHITE}TikTok Music (Track): {TColor.GREEN}{len(MusicServiceURLs.tiktokmusic_track)}\n'
        f'  {TColor.LGREEN}Total of {len(MusicServiceURLs.youtube_track + MusicServiceURLs.youtube_playlist + MusicServiceURLs.resso_track + MusicServiceURLs.resso_playlist)} item(s)'
    )

    # -----------------------------------------------------------------------------------------------------------------

    # Get YouTube URLs ------------------------------------------------------------------------------------------------
    print(
        f'{TBracket(TColor.LBLUE, "RUNNING", 1)} {TColor.BLUE}Converting into YouTube URLs...'
    )

    queries = list()

    # Get YouTube URLs from YouTube playlists -------------------------------------------------------------------------
    for playlist_url in MusicServiceURLs.youtube_playlist:
        songs = mup.get_musics_from_youtube_playlist(playlist_url)
        queries.extend(songs)
    MusicServiceURLs.all_urls.extend(queries)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(queries)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.youtube_playlist)}{TColor.WHITE} YouTube playlist(s)'
    )

    # Add YouTube URLs from YouTube tracks ----------------------------------------------------------------------------
    MusicServiceURLs.all_urls.extend(MusicServiceURLs.youtube_track)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(MusicServiceURLs.youtube_track)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.youtube_track)}{TColor.WHITE} YouTube track(s)'
    )

    # Get YouTube URLs from Resso playlists ---------------------------------------------------------------------------
    queries = [
        mup.get_youtube_url_from_query(music_name)
        for playlist_url in MusicServiceURLs.resso_playlist
        for music_name in mup.get_music_name_from_resso_playlist(playlist_url)
    ]
    MusicServiceURLs.all_urls.extend(queries)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(queries)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.resso_playlist)}{TColor.WHITE} Resso playlist(s)'
    )

    # Get YouTube URLs from Resso tracks ------------------------------------------------------------------------------
    queries = [
        mup.get_youtube_url_from_query(mup.get_music_name_from_resso_track(music_url))
        for music_url in MusicServiceURLs.resso_track
    ]
    MusicServiceURLs.all_urls.extend(queries)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(queries)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.resso_track)}{TColor.WHITE} Resso track(s)'
    )

    # Get YouTube URLs from Deezer playlists --------------------------------------------------------------------------
    queries = [
        mup.get_youtube_url_from_query(music_name)
        for playlist_url in MusicServiceURLs.deezer_playlist
        for music_name in mup.get_music_name_from_deezer_playlist(playlist_url)
    ]
    MusicServiceURLs.all_urls.extend(queries)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(queries)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.deezer_playlist)}{TColor.WHITE} Deezer playlist(s)'
    )

    # Get YouTube URLs from Deezer tracks -----------------------------------------------------------------------------
    queries = [
        mup.get_youtube_url_from_query(mup.get_music_name_from_deezer_track(music_url))
        for music_url in MusicServiceURLs.deezer_track
    ]
    MusicServiceURLs.all_urls.extend(queries)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(queries)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.deezer_track)}{TColor.WHITE} Deezer track(s)'
    )

    # Get YouTube URLs from Spotify playlists -------------------------------------------------------------------------
    queries = [
        mup.get_youtube_url_from_query(music_name)
        for playlist_url in MusicServiceURLs.spotify_playlist
        for music_name in mup.get_music_name_from_spotify_playlist(playlist_url)
    ]
    MusicServiceURLs.all_urls.extend(queries)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(queries)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.spotify_playlist)}{TColor.WHITE} Spotify playlist(s)'
    )

    # Get YouTube URLs from Spotify tracks ----------------------------------------------------------------------------
    queries = [
        mup.get_youtube_url_from_query(mup.get_music_name_from_spotify_track(music_url))
        for music_url in MusicServiceURLs.spotify_track
    ]
    MusicServiceURLs.all_urls.extend(queries)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(queries)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.spotify_track)}{TColor.WHITE} Spotify track(s)'
    )

    # Get YouTube URLs from TikTok Music playlists --------------------------------------------------------------------
    queries = [
        mup.get_youtube_url_from_query(music_name)
        for playlist_url in MusicServiceURLs.tiktokmusic_playlist
        for music_name in mup.get_music_name_from_tiktokmusic_playlist(playlist_url)
    ]
    MusicServiceURLs.all_urls.extend(queries)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(queries)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.tiktokmusic_playlist)}{TColor.WHITE} TikTok Music playlist(s)'
    )

    # Get YouTube URLs from TikTok Music tracks -----------------------------------------------------------------------
    queries = [
        mup.get_youtube_url_from_query(mup.get_music_name_from_tiktokmusic_track(music_url))
        for music_url in MusicServiceURLs.tiktokmusic_track
    ]
    MusicServiceURLs.all_urls.extend(queries)
    print(
        f'  {TColor.WHITE}Added {TColor.GREEN}{len(queries)}{TColor.WHITE} YouTube URL(s) from {TColor.GREEN}{len(MusicServiceURLs.tiktokmusic_track)}{TColor.WHITE} TikTok Music track(s)'
    )

    # -----------------------------------------------------------------------------------------------------------------

    # Fixing YouTube URLs
    print(f'  {TColor.LGREEN}Fixing {len(MusicServiceURLs.all_urls)} URL(s)', end='\r')

    # Removing duplicates and updating the list
    all_urls = list(dict.fromkeys(MusicServiceURLs.all_urls))
    removed_items = len(MusicServiceURLs.all_urls) - len(all_urls)
    MusicServiceURLs.all_urls = all_urls

    print(
        f'  {TColor.LGREEN}Total of {len(MusicServiceURLs.all_urls)} URL(s) ready to download! {TColor.GREEN}[{TColor.RED}-{removed_items}{TColor.GREEN}]'
    )

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
    total_songs_quantity = len(MusicServiceURLs.all_urls)
    if total_songs_quantity == 0:
        print(
            f'\n{TBracket(TColor.LGREEN, "SUCCESS")} {TColor.GREEN}No songs were downloaded!'
        )
    elif total_songs_quantity == 1:
        print(
            f'\n{TBracket(TColor.LGREEN, "SUCCESS")} {TColor.GREEN}The song has been successfully downloaded!'
        )
    else:
        print(
            f'\n{TBracket(TColor.LGREEN, "SUCCESS")} {TColor.GREEN}All songs have been successfully downloaded!'
        )


while True:
    app()
    key = input(
        f'{TBracket(TColor.LWHITE, "END", 1)} {TColor.WHITE}Press ENTER to restart or anything else to exit...'
    )
    if key != str():
        break
    app_utils.clsr(1)
