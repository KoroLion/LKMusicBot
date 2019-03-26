import asyncio
from youtube_dl import YoutubeDL

from os import listdir
from os.path import isfile, join

from discord import VoiceClient


class Song(object):
    def __init__(self, url, title):
        self.url = url
        self.title = title


class MusicPlayer(object):
    def __init__(self, voice_client: VoiceClient, show_song_event, music_directory: str, current_volume: float = 50):
        self.voice_client = voice_client

        self.show_song_event = show_song_event
        self.music_directory = music_directory
        self.current_volume = current_volume / 100

        self.playlist = []
        self.player = None
        self.current_song_id = 0

        self.manual_stop = False

        self.update_songs()

    async def auto_next(self):
        while True:
            await asyncio.sleep(1)
            if not self.player:
                return
            if self.player.is_done():
                await self.play_next_song()

    # asyncio.get_event_loop() in main does not finish if this is used
    def song_finished(self):
        pass
        # if not self.player:
        #     return
        # if self.player.is_done():
        #     self.play_next_song()

    def reset_player(self):
        if self.player:
            self.player.stop()
            self.player = None

    async def play(self, seconds: int = 0):
        if not self.player:
            song = self.playlist[self.current_song_id]
            song_path = song.url

            if song_path.startswith('http://') or song_path.startswith('https://'):
                b_opt = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {}'.format(seconds)
                self.player = await self.voice_client.create_ytdl_player(song_path, before_options=b_opt)
            else:
                b_opt = '-ss {}'.format(seconds)
                self.player = self.voice_client.create_ffmpeg_player(song_path, before_options=b_opt, after=self.song_finished)

            song_name = song.title

            self.player.volume = self.current_volume
            self.player.start()

            # seeking does not changes song
            if not seconds:
                self.show_song_event(song_name)

            loop = asyncio.get_event_loop()
            await loop.create_task(self.auto_next())
        else:
            self.player.resume()

    def set_volume(self, volume):
        try:
            volume = int(volume)
            if volume > 100:
                volume = 100
            elif volume < 0:
                volume = 0

            volume /= 100

            self.current_volume = volume
            if self.player:
                self.player.volume = volume
            return True
        except ValueError:
            return False

    def get_volume(self):
        return round(self.current_volume * 100)

    async def seek(self, seconds):
        try:
            seconds = int(seconds)
            self.reset_player()
            await self.play(seconds)
        except ValueError:
            pass

    def update_songs(self):
        # self.playlist = [join(self.music_directory, f) for f in listdir(self.music_directory) if isfile(join(self.music_directory, f))]
        self.playlist = []
        for f in listdir(self.music_directory):
            song_path = join(self.music_directory, f)
            if isfile(song_path):
                song = Song(song_path, f)
                self.playlist.append(song)

    async def play_next_song(self):
        self.reset_player()

        self.current_song_id += 1
        if self.current_song_id >= len(self.playlist):
            self.current_song_id = 0

        await self.play()

    async def select_song(self, number: int = 1):
        self.current_song_id = int(number) - 1
        if self.current_song_id >= len(self.playlist) or self.current_song_id < 0:
            raise Exception('Incorrect song number!')

        self.reset_player()

        await self.play()

    async def play_previous_song(self):
        self.reset_player()

        self.current_song_id -= 1
        if self.current_song_id < 0:
            self.current_song_id = len(self.playlist) - 1

        await self.play()

    def pause(self):
        self.player.pause()

    def add_to_playlist(self, song_path):
        ydl = YoutubeDL({})

        try:
            info = ydl.extract_info(song_path, download=False)
            title = info.get('title', 'WARN: Title was not found!')
            song = Song(song_path, title)
            self.playlist.append(song)
            # info.get('thumbnail', '')
            return title
        except Exception:
            return False

    def delete_from_playlist(self, sid: int):
        try:
            sid = int(sid) - 1
            if sid >= len(self.playlist) or sid < 0:
                raise ValueError('Invalid index!')
            song = self.playlist.pop(sid)
            return song
        except Exception:
            return False

    def get_playlist_titles(self):
        song_names = []
        for song in self.playlist:
            song_names.append(song.title)

        return song_names

