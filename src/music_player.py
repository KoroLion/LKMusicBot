import asyncio

from os import listdir
from os.path import isfile, join, basename

from discord import VoiceClient


class MusicPlayer(object):
    def __init__(self, voice_client: VoiceClient, show_song_event, music_directory: str, default_volume: float = 0.5):
        self.voice_client = voice_client

        self.show_song_event = show_song_event
        self.music_directory = music_directory
        self.default_volume = default_volume

        self.songs = None
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
                self.play_next_song()

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

    def play(self, second: int = 0):
        if not self.player:
            song_path = self.songs[self.current_song_id]

            self.player = self.voice_client.create_ffmpeg_player(song_path, before_options='-ss {}'.format(second), after=self.song_finished)
            self.player.volume = self.default_volume
            self.player.start()

            # seeking does not changes song
            if not second:
                self.show_song_event(basename(song_path))

            loop = asyncio.get_event_loop()
            loop.create_task(self.auto_next())
        else:
            self.player.resume()

    def set_volume(self, volume):
        try:
            volume = int(volume)
            self.player.volume = volume / 100
        except ValueError:
            pass

    def get_volume(self):
        return round(self.player.volume * 100)

    def seek(self, seconds):
        try:
            sec = int(seconds)
            self.reset_player()
            self.play(sec)
        except ValueError:
            pass

    def update_songs(self):
        self.songs = [join('music', f) for f in listdir(self.music_directory) if isfile(join(self.music_directory, f))]

    def play_next_song(self):
        self.reset_player()

        self.current_song_id += 1
        if self.current_song_id >= len(self.songs):
            self.current_song_id = 0

        self.play()

    def play_previous_song(self):
        self.reset_player()

        self.current_song_id -= 1
        if self.current_song_id < 0:
            self.current_song_id = len(self.songs) - 1

        self.play()

    def pause(self):
        self.player.pause()
