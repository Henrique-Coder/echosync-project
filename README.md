<p align='center'>
    <a href='https://github.com/Henrique-Coder/echosync-project/blob/main/README.md'>
        <img src='https://img.shields.io/badge/DOCS-soon...-lightgray?style=for-the-badge' alt='Documentation'></a>
    <a href='https://www.python.org/downloads/release/python-3114/'>
        <img src='https://img.shields.io/badge/Python-3.11.4-blue?style=for-the-badge&logo=python' alt='Python 3.11.4'></a>
    <a href='https://opensource.org/license/mit/'>
        <img src='https://img.shields.io/github/license/Henrique-Coder/echosync-project?style=for-the-badge&logo=github&color=blue' alt='GitHub License'></a>
    <a href='https://github.com/Henrique-Coder/echosync-project/issues'>
        <img src='https://img.shields.io/github/issues/Henrique-Coder/echosync-project?style=for-the-badge&logo=github&color=blue' alt='GitHub Issues'></a>

<center>

## ECS-P ・ EchoSync Project (All for epic music!)

</center>

<center>

**ECS-P** is an open source project originally created in Python 3.11.4, which allows you to download music playlists in
a fast and intuitive way. Using [YouTube](https://www.youtube.com/) as a music search source,
the [yt-dlp](https://pypi.org/project/yt-dlp/) library to download the songs and [FFmpeg](https://ffmpeg.org/) to
re-encode the songs, enhancing their metadata and overall file.

</center>

<br>
<p align='center'>
    <a href='https://github.com/Henrique-Coder/echosync-project'>
        <img src='favicon.ico' width='72' height='72' alt='Favicon'></a>
<br><br>

---

<p align='center'>
  <a href='https://github.com/Henrique-Coder/echosync-project/releases/latest'>
    <img src='https://img.shields.io/github/v/release/Henrique-Coder/echosync-project?color=red&style=for-the-badge' alt='GitHub release (latest by date)'></a><p>

### Available features (v1.1.5)

In the list below, it shows everything that **ECS-P** can do with each music platform...

- It can download songs by song name only;
- Can download a list of songs by a text file;
- Supports downloading individual songs or playlists
  from [YouTube](https://www.youtube.com/), [YouTube Music](https://music.youtube.com/), [Resso](https://www.resso.com/), [Deezer](https://www.deezer.com/), [Spotify](https://www.spotify.com/)
  and [TikTok Music](https://music.tiktok.com/);
- And much more!

* **Note 1:** _The program will automatically detect the music platform by the link used, so do not use link shorteners
  to modify it. Unavailable links or platforms will be automatically rejected. Texts detected as the title of a song
  will automatically be added to the download queue and the search for the song will take place via YouTube._
* **Note 2:** _The program uses proprietary web scrapping techniques to extract the name/author of the song on the
  detected platform and will download it directly from YouTube._

### _Possible_ future implementations

Later on, I plan to implement more music platforms, such as:

<p align='left'>
    <img src=".github/music_platforms/todo/soundcloud.png" alt="Soundcloud" style="display:inline-block; width:24px; height:24px; margin-right: 6px;">
    <img src=".github/music_platforms/todo/tidal.png" alt="Tidal" style="display:inline-block; width:24px; height:24px; margin-right: 6px;">
    <img src=".github/music_platforms/todo/apple_music.png" alt="Apple Music" style="display:inline-block; width:24px; height:24px; margin-right: 6px;">
    <img src=".github/music_platforms/todo/amazon_music.png" alt="Amazon Music" style="display:inline-block; width:24px; height:24px; margin-right: 6px;">
    <img src=".github/music_platforms/todo/napster.png" alt="Napster" style="display:inline-block; width:24px; height:24px; margin-right: 6px;">
</p>
<br>

---

### How to use? (running from the executable)

1. Download the latest version of the
   program [here](https://github.com/Henrique-Coder/echosync-project/releases/latest);
2. Run the binary file;
3. Follow the instructions on the terminal screen;
4. Enjoy your music! :D

### How to use? (running from source code)

1. Clone the repository to your local machine ・ `git clone https://github.com/Henrique-Coder/echosync-project.git`;
2. Go to the main directory ・ `cd echosync-project`;
3. Install the project dependencies ・ `pip install -r requirements.txt`;
4. Go to the project source directory ・ `cd src`;
5. Run the main file ・ `python app.py`;
6. Follow the instructions on the terminal screen;
7. Enjoy your music! :D

<br>

---

### Credits

- Many thanks to my brother _Felipe_ for the gigantic help ❤️ ・ [GitHub](https://github.com/mindwired) & [LinkedIn](https://www.linkedin.com/in/cidadedolag).

### Disclaimer

Please note that downloading copyrighted music may be illegal in your country.
This tool is designed for educational purposes only, and to demonstrate how you can extract accurate song and author information from websites and music services.
Please support the artists by purchasing their music and respecting copyrights.
