import configparser

BOT_VERSION = '0.4.1'
RELEASE_DATE = '28.03.2019'

config = configparser.ConfigParser()
config.read('./settings.ini', encoding='utf8')
config = config['TEST']

DEBUG = config.getboolean('Debug', True)
MUSIC_DIRECTORY = config.get('MusicDirectory', 'music')
CONTROL_CHANNEL_PREFIX = config.get('ControlChannelPrefix', '🎵')
DEFAULT_VOLUME = int(config.get('DefaultVolume', 30))
CURRENT_SONG_IN_STATUS = config.getboolean('CurrentSongInStatus', True)
NOTIFY_INVALID_COMMAND = config.getboolean('NotifyInvalidCommand', True)

if DEBUG:
    BOT_TOKEN = config.get('BotTokenDebug', None)
else:
    BOT_TOKEN = config.get('BotTokenProd', None)
