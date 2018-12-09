import asyncio
from os import path

import discord
from discord import Message, Client

import settings
from music_player import MusicPlayer
from help_message import help_message

bot = Client()
voice_channels = {}
music_players = {}
loop = None


def get_bot_control_channel(channels):
    for channel in channels:
        if channel.name.startswith(settings.CONTROL_CHANNEL_PREFIX) and str(channel.type) == 'text':
            return channel

    return None


def next_song_event_generator(text_channel):
    def next_song_event(song_name):
        global loop
        if song_name and loop:
            loop.create_task(bot.send_message(text_channel, 'Now playing: **' + song_name + '**'))
            if settings.CURRENT_SONG_IN_STATUS:
                loop.create_task(bot.change_presence(game=discord.Game(name=song_name)))

    return next_song_event


async def incorrect_message(message):
    await bot.delete_message(message)
    if settings.NOTIFY_INVALID_COMMAND:
        await bot.send_message(message.author, 'Sorry, but I deleted your message, because your command is invalid. Send "help" to get help.\nHere is your message: \n*{}*'.format(message.content))

        
async def disconnect_player(server_id):
    m_player = music_players.get(server_id, None)
    m_player.reset_player()
    await m_player.voice_client.disconnect()
    del music_players[server_id]
    del voice_channels[server_id]
    await bot.change_presence(game=discord.Game(name='v. {}'.format(settings.BOT_VERSION)))


@bot.event
async def on_message(message: Message):
    if message.author.id == bot.user.id:
        return
    if not message.content:
        return

    content = message.content.split(' ')
    command = content[0]
    if len(content) > 1:
        args = content[1:]
    else:
        args = None

    if message.channel.is_private:
        if command != 'help':
            await bot.send_message(message.author, "I didn't get that. But there are available commands:")
        await bot.send_message(message.author, help_message)

        return

    control_channel = get_bot_control_channel(message.server.channels)

    if not control_channel:
        return
    if control_channel.id != message.channel.id:
        return

    m_player = music_players.get(message.server.id, None)
    voice_channel = message.author.voice.voice_channel

    if command == 'summon' or command == 'summoning jutsu':
        if voice_channel:
            if m_player:
                await m_player.voice_client.disconnect()
                m_player.voice_client = await bot.join_voice_channel(voice_channel)
            else:
                voice_client = await bot.join_voice_channel(voice_channel)
                m_player = MusicPlayer(
                    voice_client,
                    next_song_event_generator(control_channel),
                    settings.MUSIC_DIRECTORY,
                    settings.DEFAULT_VOLUME
                )

                music_players.update({message.server.id: m_player})
                voice_channels.update({message.server.id: voice_channel})

            username = message.author.nick if message.author.nick else message.author.name
            await bot.send_message(control_channel, 'At your service, sir {}.'.format(username))
        else:
            await bot.send_message(control_channel, 'Unable to join: unknown voice channel!')
    elif command == 'help':
        await bot.send_message(message.author, help_message)
    elif command == 'clear_messages':
        if not message.author.permissions_in(control_channel).manage_messages:
            return
        await bot.purge_from(control_channel, limit=50)
    elif command == 'update_songs':
        if not message.author.permissions_in(control_channel).manage_messages:
            return
        m_player.update_songs()
    elif m_player:
        if command == 'bye':
            await disconnect_player(message.server.id)
        elif command == 'play':
            m_player.play()
        elif command == 'seek':
            if args:
                m_player.seek(args[0])
        elif command == 'volume':
            if args:
                m_player.set_volume(args[0])
            else:
                await bot.send_message(control_channel, 'Current volume is {}'.format(m_player.get_volume()))
        elif command == 'pause':
            m_player.pause()
        elif command == 'stop':
            await bot.change_presence(game=discord.Game(name='v. {}'.format(settings.BOT_VERSION)))
            m_player.reset_player()
        elif command == 'next':
            m_player.play_next_song()
        elif command == 'prev':
            m_player.play_previous_song()
        else:
            await incorrect_message(message)
    else:
        await incorrect_message(message)


async def check_online():
    while True:
        to_leave = []
        for server_id in voice_channels:
            voice_channel = voice_channels.get(server_id, None)
            if voice_channel:
                if len(voice_channel.voice_members) < 2:
                    to_leave.append(server_id)

        for server_id in to_leave:
            await disconnect_player(server_id)

        await asyncio.sleep(1)


@bot.event
async def on_ready():
    global loop

    print('Logged in as {} ({})'.format(bot.user.name, bot.user.id))
    await bot.change_presence(game=discord.Game(name='v. {}'.format(settings.BOT_VERSION)))
    loop = asyncio.get_event_loop()
    loop.create_task(check_online())

    print('Control channel prefix: {}'.format(settings.CONTROL_CHANNEL_PREFIX))
    print('Music directory: {}'.format(path.abspath(settings.MUSIC_DIRECTORY)))
    print('Bot is member of {} servers'.format(len(bot.servers)))

bot.run(settings.BOT_TOKEN)
