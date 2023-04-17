from os import system, makedirs, environ, pathsep, path, getcwd, remove
from pathlib import Path
from re import sub, findall
from shutil import rmtree
from time import sleep, time
from tkinter import Tk, filedialog

from colorama import init as colorama_init, Fore
from music_tag import load_file as tag_load_file
from pytube import YouTube, extract
from pytube.exceptions import VideoUnavailable, AgeRestrictedError, LiveStreamError, VideoPrivate, \
    RecordingUnavailable, MembersOnly, VideoRegionBlocked
from requests import get
from tqdm import tqdm
from youtubesearchpython import SearchVideos
from zstd import ZSTD_uncompress


# Inicializa o tempo de execucao do programa
start_time = time()

# Configuracoes padrao
success_downloads = 0
already_exists = 0
failed_downloads = 0
total_requests = 0

# Inicializa o colorama
colorama_init(autoreset=True)

# Seta as variaveis para o diretorio do programa
app_name = 'Batch Music Downloader'
userprofile_dir = environ['userprofile']
app_dir = Path(fr'{userprofile_dir}\AppData\Local\{app_name}')

# Cria as pastas necessárias
makedirs(fr'{app_dir}\dependencies', exist_ok=True)
makedirs(fr'{app_dir}\assets', exist_ok=True)

makedirs('songs', exist_ok=True)
makedirs(r'.temp\songs', exist_ok=True)
makedirs(r'.temp\thumbnails', exist_ok=True)

def cl(jump_lines=0):
    system('cls || clear')

    for num in range(jump_lines):
        print()

def convert_seconds_to_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    # Formatação para dois dígitos com zero à esquerda
    hours_str = str(hours).zfill(2)
    minutes_str = str(minutes).zfill(2)
    seconds_str = str(seconds).zfill(2)

    # Formata a string para o formato 'hh:mm:ss' e retorna o resultado
    formatted_time = f'{hours_str}:{minutes_str}:{seconds_str}'
    return formatted_time

def tqdm_custom_bar(current, total, width=40, char=''):
    filled_length = int(width * current / total)
    empty_length = width - filled_length
    bar = char * filled_length + ' ' * empty_length
    return f'[{bar}]'

def download_ffmpeg():
    # Baixando o FFMPEG compactado [Tamanho compactado: ~41MB]
    ffmpeg_exe_zst = Path(fr'{app_dir}\dependencies\ffmpeg.exe.zst')
    ffmpeg_exe = Path(fr'{app_dir}\dependencies\ffmpeg.exe')

    if not ffmpeg_exe.is_file():
        ffmpeg_url = 'https://drive.google.com/uc?export=download&id=16Ob9qv7uwLWqcMOwTOKeC9p52accn-wO'

        r = get(ffmpeg_url, allow_redirects=True, stream=True)
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024  # Tamanho do bloco de download

        # Configurar o formato da barra de progresso e a animação
        print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}!{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}O FFMPEG não foi encontrado no local padrão! Então, será baixado automaticamente...')
        bar_format = '★ Progress › {bar} ‹ {percentage:3.1f}% • Rate|Downloaded|Total: {rate_fmt}{postfix}|{n_fmt}|{total_fmt} — Elapsed|Remaining: {elapsed}|{remaining}'
        anim_rotation_dot = ' ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏━'

        with open(ffmpeg_exe_zst, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True, dynamic_ncols=True,
                                                   bar_format=bar_format, ascii=anim_rotation_dot,
                                                   mininterval=0.1, smoothing=True) as pbar:
            for data in r.iter_content(block_size):
                f.write(data)
                pbar.set_description(tqdm_custom_bar(pbar.n, total_size))
                pbar.update(len(data))

        # Descompactando o FFMPEG com o ZSTD [Tamanho descompactado: ~123MB]
        with open(fr'{app_dir}\dependencies\ffmpeg.exe.zst', mode='rb') as fi:
            with open(fr'{app_dir}\dependencies\ffmpeg.exe', mode='wb') as fo:
                fo.write(ZSTD_uncompress(fi.read()))

        # Deletando o arquivo FFMPEG compactado
        remove(fr'{app_dir}\dependencies\ffmpeg.exe.zst')
    environ['PATH'] += pathsep + path.join(getcwd(), fr'{app_dir}\dependencies')
    print()

def format_string(title):
    # Formata a string para ser compativel com os diretorios do Windows
    new_title = ''
    for ch in title:
        if ch in 'aáàâãbcçdeéèêfghiíìîjklmnoóòôõpqrstuúùûvwxyzAÁÀÂÃBCÇDEÉÈÊFGHIÍÌÎJKLMNOÓÒÔÕPQRSTUÚÙÛVWXYZ0123456789-_()[]{}# ':
            new_title += ch
    new_title = sub(' +', ' ', new_title).strip()
    return new_title

def get_thumbnail_url(url, resolution, hostname):
    # Retorna a URL da thumbnail

    # website >> 'img.youtube.com' ou 'i.ytimg.com'
    # resolution >> 'maxresdefault', 'sddefault', 'hqdefault', 'mqdefault', 'default'

    thumbnail_url = f'https://{hostname}/vi/{extract.video_id(url)}/{resolution}.jpg'
    return thumbnail_url

def get_youtube_url(query):
    # Busca a URL do video no YouTube
    try:
        search = SearchVideos(query, offset=1, mode='dict', max_results=1)
        results = search.result()
        return str(results['search_result'][0]['link'])

    except Exception as e:
        print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}Erro ao buscar a URL da música no YouTube! Erro: {Fore.LIGHTBLUE_EX}{e}\n')
        pass

def enchance_music_file(yt, music_title):
    # Globaliza as variaveis
    global success_downloads

    # Codificar o arquivo de musica (printar apenas uma linha do output do ffmpeg)
    system(fr'ffmpeg -i ".temp\songs\{music_title}.mp3" -b:a 320k -vn "songs\{music_title}.mp3" -y -hide_banner -loglevel quiet -stats')

    # Adiciona metadados ao arquivo de musica
    publish_year = str(yt.publish_date).split('-')[0]

    f = tag_load_file(fr'songs\{music_title}.mp3')
    f['artwork'] = open(fr'.temp\thumbnails\{music_title}.jpg', 'rb').read()
    f['tracktitle'] = music_title
    f['artist'] = format_string(yt.author)
    f['year'] = publish_year
    f['albumartist'] = format_string(yt.author)
    f['genre'] = 'Music'
    f.save()

    # Deleta o arquivo de musica baixado pelo pytube
    remove(fr'.temp\songs\{music_title}.mp3')

    # Deleta a thumbnail baixada
    remove(fr'.temp\thumbnails\{music_title}.jpg')

    print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTGREEN_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTGREEN_EX}Música salva com sucesso!\n')

    success_downloads += 1

def download_music(url, now_downloading, total_urls):
    # Globaliza as variaveis
    global already_exists, failed_downloads, total_requests

    total_attempts = 16
    retry_attempts = total_attempts
    retry_delay = 3

    while retry_attempts > 0:
        try:
            total_requests += 1
            retry_attempts -= 1
            yt = YouTube(url)
            music_title = format_string(yt.title)
            break

        except VideoRegionBlocked:
            print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}Erro ao acessar o URL: {Fore.LIGHTBLUE_EX}"{url}"{Fore.LIGHTRED_EX}, pois a música está {Fore.LIGHTBLUE_EX}bloqueada na sua região{Fore.LIGHTRED_EX}! Pulando para o próximo da lista...\n')
            failed_downloads += 1
            return
        except AgeRestrictedError:
            print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}Erro ao acessar o URL: {Fore.LIGHTBLUE_EX}"{url}"{Fore.LIGHTRED_EX}, pois a música é {Fore.LIGHTBLUE_EX}restrita a maiores de 18 anos{Fore.LIGHTRED_EX} e não pode ser baixada anonimamente! Pulando para o próximo da lista...\n')
            failed_downloads += 1
            return
        except LiveStreamError:
            print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}Erro ao acessar o URL: {Fore.LIGHTBLUE_EX}"{url}"{Fore.LIGHTRED_EX}, pois a música é {Fore.LIGHTBLUE_EX}ao vivo{Fore.LIGHTRED_EX} e não é possível baixá-la! Pulando para o próximo da lista...\n')
            failed_downloads += 1
            return
        except VideoPrivate:
            print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}Erro ao acessar o URL: {Fore.LIGHTBLUE_EX}"{url}"{Fore.LIGHTRED_EX}, pois a música é {Fore.LIGHTBLUE_EX}privada{Fore.LIGHTRED_EX} e não é possível acessá-la! Pulando para o próximo da lista...\n')
            failed_downloads += 1
            return
        except RecordingUnavailable:
            print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}Erro ao acessar o URL: {Fore.LIGHTBLUE_EX}"{url}"{Fore.LIGHTRED_EX}, pois a música está {Fore.LIGHTBLUE_EX}indisponível{Fore.LIGHTRED_EX}! Pulando para o próximo da lista...\n')
            failed_downloads += 1
            return
        except MembersOnly:
            print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}Erro ao acessar o URL: {Fore.LIGHTBLUE_EX}"{url}"{Fore.LIGHTRED_EX}, pois a música é {Fore.LIGHTBLUE_EX}exclusiva para membros{Fore.LIGHTRED_EX} e não pode ser baixada anonimamente! Pulando para o próximo da lista...\n')
            failed_downloads += 1
            return
        except VideoUnavailable:
            print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}Erro ao acessar o URL: {Fore.LIGHTBLUE_EX}"{url}"{Fore.LIGHTRED_EX}, pois a música está {Fore.LIGHTBLUE_EX}indisponível{Fore.LIGHTRED_EX}! Pulando para o próximo da lista...\n')
            failed_downloads += 1
            return

        except Exception as e:
            if retry_attempts == 0:
                print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}Pulando para o próximo da lista...\n')
                return

            else:
                print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}Erro na {Fore.LIGHTBLUE_EX}{total_attempts-retry_attempts}/{total_attempts-1}º {Fore.LIGHTRED_EX}tentativa: {Fore.LIGHTBLUE_EX}"{e}"{Fore.LIGHTRED_EX}! Tentando novamente...')
                sleep(retry_delay)

    # Baixa a musica do YouTube
    try:
        thumbnail_url = get_thumbnail_url(url, resolution='maxresdefault', hostname='i.ytimg.com')

        # Baixa a musica (dir: 'songs')
        if Path(fr'songs\{music_title}.mp3').is_file():
            print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTYELLOW_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTYELLOW_EX}Música {Fore.LIGHTBLUE_EX}"{music_title}" {Fore.LIGHTYELLOW_EX}já foi baixada anteriormente!\n')
            already_exists += 1
            return

        else:
            print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTYELLOW_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTYELLOW_EX}Baixando música {Fore.LIGHTBLUE_EX}"{music_title}"{Fore.LIGHTYELLOW_EX}...')

            yt_stream = yt.streams.filter(only_audio=True).get_audio_only()
            yt_stream.download(filename=music_title + '.mp3', output_path='.temp\songs')

            # Baixa a thumbnail da musica (dir: '.temp') caso a musica tenha sido baixada
            r = get(thumbnail_url, allow_redirects=True)
            open(fr'.temp\thumbnails\{music_title}.jpg', 'wb').write(r.content)

            enchance_music_file(yt, music_title)

    except Exception as e:
        print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}{now_downloading}/{total_urls}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}Erro ao baixar a musica {Fore.LIGHTBLUE_EX}"{music_title}"{Fore.LIGHTRED_EX}! Erro: {Fore.LIGHTBLUE_EX}{e}\n')

# Baixa o FFMPEG
download_ffmpeg()

#def from_local_file():


# Pergunta se o usuário quer baixar as músicas de um arquivo de texto ou escrever manualmente
print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTYELLOW_EX}?{Fore.LIGHTWHITE_EX}] {Fore.LIGHTYELLOW_EX}Você pode baixar as músicas de um {Fore.LIGHTCYAN_EX}arquivo de texto local {Fore.LIGHTYELLOW_EX}ou {Fore.LIGHTCYAN_EX}escrever manualmente{Fore.LIGHTYELLOW_EX}.\n')

print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTGREEN_EX}!{Fore.LIGHTWHITE_EX}] {Fore.LIGHTWHITE_EX}Para selecionar um arquivo de texto local, deixe em branco e pressione ENTER.')
print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTGREEN_EX}!{Fore.LIGHTWHITE_EX}] {Fore.LIGHTWHITE_EX}Para escrever manualmente, digite alguma URL (do YouTube) ou nome de música e pressione ENTER.\n')

print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTRED_EX}0{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}Lista de URLs/Queries — Para escolher um arquivo de texto local, deixe em branco e pressione ENTER.')
user_response = input(f'\r{Fore.LIGHTWHITE_EX}›{Fore.LIGHTBLUE_EX} ')

user_response = user_response.strip()
if user_response == '':
    # Limpa a tela e pula uma linha
    cl(jump_lines=1)

    print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTYELLOW_EX}!{Fore.LIGHTWHITE_EX}] {Fore.LIGHTYELLOW_EX}Abrindo o explorador de arquivos para você selecionar o arquivo de texto local...\n')

    # Inicializa a janela Tkinter e oculta-a
    root = Tk()
    root.withdraw()

    # Baixa o ícone da janela de dialogo caso não exista
    explorer_ico_url = 'https://raw.githubusercontent.com/Henrique-Coder/batch-music-downloader/main/assets/explorer.ico'
    explorer_ico_dir = fr'{app_dir}\assets\explorer.ico'

    if not Path(explorer_ico_dir).is_file():
        r = get(explorer_ico_url, allow_redirects=True)

        with open(explorer_ico_dir, 'wb') as fo:
            fo.write(r.content)

    root.iconbitmap(explorer_ico_dir)

    # Abre uma janela de diálogo para selecionar o arquivo de entrada
    input_file_path = filedialog.askopenfilename(title='Selecione um arquivo de texto com as URLs/Queries',
                                                 filetypes=[('Arquivo de Texto', '*.txt')])

    # Limpa a tela e pula uma linha
    cl(jump_lines=1)

    # Abre o arquivo no modo de leitura, especificando a codificação como UTF-8
    with open(input_file_path.strip(), 'r', encoding='utf-8') as query_list:
        query_list = [line.strip() for line in query_list.readlines()]
        query_list = [line for line in query_list if line != '']
        total_urls = len(query_list)
        now_downloading = 0

        print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTGREEN_EX}#{Fore.LIGHTWHITE_EX}] {Fore.LIGHTGREEN_EX}Total de URLs: {Fore.LIGHTBLUE_EX}{total_urls}\n')

        for query in query_list:
            sleep(1)

            yt_url_regex = r'(?:https?://)?(?:www\.)?(?:m\.)?(?:youtu\.be/|youtube\.com/(?:watch\?(?=.*v=\w+)(?:\S+)?v=|embed/|v/)?)([\w-]{11})'
            url_match = findall(yt_url_regex, query)

            if url_match:
                now_downloading += 1

                url = query.strip()
                download_music(url, now_downloading, total_urls)

            else:
                now_downloading += 1

                url = get_youtube_url(query).strip()
                download_music(url, now_downloading, total_urls)

else:
    query_list = []

    while user_response != '':
        query_list.append(user_response)
        user_response = input(f'{Fore.LIGHTWHITE_EX}›{Fore.LIGHTBLUE_EX} ')

    total_urls = len(query_list)
    now_downloading = 0

    # Limpa a tela e pula uma linha
    cl(jump_lines=1)

    print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTGREEN_EX}#{Fore.LIGHTWHITE_EX}] {Fore.LIGHTGREEN_EX}Total de URLs: {Fore.LIGHTBLUE_EX}{total_urls}\n')

    for query in query_list:
        sleep(1)

        yt_url_regex = r'(?:https?://)?(?:www\.)?(?:m\.)?(?:youtu\.be/|youtube\.com/(?:watch\?(?=.*v=\w+)(?:\S+)?v=|embed/|v/)?)([\w-]{11})'
        url_match = findall(yt_url_regex, query)

        if url_match:
            now_downloading += 1

            url = query.strip()
            download_music(url, now_downloading, total_urls)

        else:
            now_downloading += 1

            url = get_youtube_url(query).strip()
            download_music(url, now_downloading, total_urls)

# Deletando os arquivos temporarios
rmtree(fr'.temp', ignore_errors=True)

print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTGREEN_EX}T{Fore.LIGHTWHITE_EX}] {Fore.LIGHTGREEN_EX}Tempo de execução: {Fore.LIGHTBLUE_EX}{convert_seconds_to_time(time() - start_time)}')
print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTGREEN_EX}|{Fore.LIGHTWHITE_EX}] {Fore.LIGHTGREEN_EX}Salvas: {Fore.LIGHTBLUE_EX}{success_downloads}')
print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTGREEN_EX}|{Fore.LIGHTWHITE_EX}] {Fore.LIGHTGREEN_EX}Ignoradas: {Fore.LIGHTBLUE_EX}{already_exists}')
print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTGREEN_EX}|{Fore.LIGHTWHITE_EX}] {Fore.LIGHTGREEN_EX}Falhas: {Fore.LIGHTBLUE_EX}{failed_downloads}')
print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTGREEN_EX}L{Fore.LIGHTWHITE_EX}] {Fore.LIGHTGREEN_EX}Tentativas falhas: {Fore.LIGHTBLUE_EX}{total_requests - (success_downloads + already_exists + failed_downloads)}')

input()
