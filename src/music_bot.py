from discord import Client, Game

from settings import BOT_VERSION


class MusicBot(Client):
    def __init__(self):
        super().__init__()

        self.voice_channels = {}
        self.music_players = {}

    def get_empty_servers_id(self) -> list:
        to_leave = []
        for server_id in self.voice_channels:
            voice_channel = self.voice_channels.get(server_id, None)
            if voice_channel:
                if len(voice_channel.voice_members) < 2:
                    to_leave.append(server_id)

        return to_leave

    async def disconnect_from_server(self, server_id):
        m_player = self.music_players.get(server_id, None)
        m_player.reset_player()
        await m_player.voice_client.disconnect()
        del self.music_players[server_id]
        del self.voice_channels[server_id]
        await self.change_presence(game=Game(name='v. {}'.format(BOT_VERSION)))
