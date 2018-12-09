from private_settings import BOT_TOKEN_DEBUG, BOT_TOKEN_PROD

try:
    from debug import DEBUG
except ImportError:
    DEBUG = False

BOT_VERSION = '0.2.1'

MUSIC_DIRECTORY = 'music'
CONTROL_CHANNEL_PREFIX = '🎵'
DEFAULT_VOLUME = 0.3
CURRENT_SONG_IN_STATUS = True
NOTIFY_INVALID_COMMAND = True

if DEBUG:
    BOT_TOKEN = BOT_TOKEN_DEBUG
else:
    BOT_TOKEN = BOT_TOKEN_PROD
