import asyncio
from os import path

import discord
from discord import Message

import settings

from music_bot import MusicBot
from music_player import MusicPlayer
from help_message import help_message


bot = MusicBot()


def get_bot_control_channel(channels):
    for channel in channels:
        if channel.name.startswith(settings.CONTROL_CHANNEL_PREFIX) and str(channel.type) == 'text':
            return channel

    return None


def next_song_event_generator(text_channel):
    def next_song_event(song_name):
        if song_name:
            loop = asyncio.get_event_loop()
            loop.create_task(bot.send_message(text_channel, 'Now playing: **' + song_name + '**'))
            if settings.CURRENT_SONG_IN_STATUS:
                loop.create_task(bot.change_presence(game=discord.Game(name=song_name)))

    return next_song_event


async def incorrect_message(message):
    await bot.delete_message(message)
    if settings.NOTIFY_INVALID_COMMAND:
        await bot.send_message(message.author, 'Sorry, but I deleted your message, because your command is invalid. Send "help" to get help.\nHere is your message: \n*{}*'.format(message.content))


@bot.event
async def on_message(message: Message):
    if message.author.id == bot.user.id:
        return

    control_channel = get_bot_control_channel(message.server.channels)

    if not control_channel:
        return
    if control_channel.id != message.channel.id:
        return

    if not message.content:
        await bot.delete_message(message)
        return

    content = message.content.split(' ')
    command = content[0].lower()
    if len(content) > 1:
        args = content[1:]
    else:
        args = None

    if message.channel.is_private:
        if command != 'help':
            await bot.send_message(message.author, "I didn't get that. But there are available commands:")
        await bot.send_message(message.author, help_message)

        return

    m_player = bot.music_players.get(message.server.id, None)
    user_voice_channel = message.author.voice.voice_channel
    bot_voice_channel = bot.voice_channels.get(message.server.id, None)

    if command == 'summon' or command == 'summoning jutsu':
        if user_voice_channel:
            if m_player:
                await m_player.voice_client.disconnect()
                m_player.voice_client = await bot.join_voice_channel(user_voice_channel)
            else:
                voice_client = await bot.join_voice_channel(user_voice_channel)
                m_player = MusicPlayer(
                    voice_client,
                    next_song_event_generator(control_channel),
                    settings.MUSIC_DIRECTORY,
                    settings.DEFAULT_VOLUME
                )

                bot.music_players.update({message.server.id: m_player})
                bot.voice_channels.update({message.server.id: user_voice_channel})

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
    elif m_player and user_voice_channel == bot_voice_channel:
        if command == 'bye':
            await bot.disconnect_from_server(message.server.id)
        elif command == 'play':
            success = await m_player.play()
            if not success:
                await incorrect_message(message)
        elif command == 'seek' and args:
            await m_player.seek(args[0])
        elif command == 'volume':
            if args:
                success = m_player.set_volume(args[0])
                if not success:
                    await incorrect_message(message)
                else:
                    await bot.send_message(control_channel, 'New volume is {}%'.format(m_player.get_volume()))
            else:
                await bot.send_message(control_channel, 'Current volume is {}%'.format(m_player.get_volume()))
        elif command == 'pause':
            m_player.pause()
        elif command == 'stop':
            await bot.change_presence(game=discord.Game(name='v. {}'.format(settings.BOT_VERSION)))
            m_player.reset_player()
        elif command == 'next':
            await m_player.play_next_song()
        elif command == 'prev':
            await m_player.play_previous_song()
        elif command == 'add' and args:
            success = m_player.add_to_playlist(args[0])
            if not success:
                await incorrect_message(message)
        elif command == 'delete':
            if args:
                song = await m_player.delete_from_playlist(args[0])
            else:
                song = await m_player.delete_from_playlist()

            if not song:
                await incorrect_message(message)
            else:
                # todo: execute playlist command here
                await bot.send_message(control_channel, '***{}.** {} was deleted from playlist!*'.format(args[0], song.title))
        elif command == 'playlist':
            plist_msg = ''
            i = 1
            for song_title in m_player.get_playlist_titles():
                if m_player.current_song_id == i - 1:
                    song_title = '**' + song_title + '**'
                else:
                    song_title = '*' + song_title + '*'

                plist_msg += '**{}**. {}\n'.format(i, song_title)
                i += 1
            if plist_msg:
                await bot.send_message(control_channel, plist_msg)
            else:
                await bot.send_message(control_channel, '*The playlist is empty!*')
        elif command == 'select' and args:
            try:
                await m_player.select_song(args[0])
            except Exception:
                await incorrect_message(message)
        else:
            await incorrect_message(message)
    else:
        await incorrect_message(message)


async def check_online():
    while True:
        to_leave = bot.get_empty_servers_id()
        for server_id in to_leave:
            await bot.disconnect_from_server(server_id)

        await asyncio.sleep(10)


@bot.event
async def on_ready():
    print('Logged in as {} ({})'.format(bot.user.name, bot.user.id))
    print('Control channel prefix: {}'.format(settings.CONTROL_CHANNEL_PREFIX))
    print('Music directory: {}'.format(path.abspath(settings.MUSIC_DIRECTORY)))
    print('Bot is a member of {} guilds.'.format(len(bot.servers)))

    await bot.change_presence(game=discord.Game(name='v. {}'.format(settings.BOT_VERSION)))
    loop = asyncio.get_event_loop()
    await loop.create_task(check_online())

bot.run(settings.BOT_TOKEN)
