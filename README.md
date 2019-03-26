# LioKor Music Bot
Simple Discord bot written in Python 3 for playing music files (.mp3, .flac, ...) on a discord server.

### Commands:
- **summon** - bot joins voice channel in which author of message is
- **bye** - bot leaves voice channel
- **play** - start playing music from directory
- **next** - next song in a playlist
- **prev** - previous song
- **stop** - stop playing and reset to first song
- **volume [int]** - set volume to [int] (from 0 to 100). Without [int] - returns current volume.
- **seek [int]** - scroll song to [int] seconds from beginning 
- **pause** - pause playing and stay at the same place of song
- **playlist** - shows current playlist
- **select [int]** - selects and plays song number [int]
- **add [url]** - adds song from [url] to an end of a playlist
- **delete [int]** - deletes song number [int]
- **clear_messages** - remove 50 latest messages in music channel. *User must have "Manage messages" permission.*
- **update_songs** - updates songs from directory. *User must have "Manage messages" permission.*

Commands received through text channel with prefix, which can be specified in settings (default 🎵 - so all messages in, for example, "🎵music" channel are commands for the bot). 

Those, who have right to write in this channel, have right to control the bot.

### Installation (Ubuntu):
1. Remove debug.py or change debug to false to run in production mode.
2. Install python libs: 
```
pip3 install -r requirements.txt
```
2. Install opus library and avconv: 
```
sudo apt-get update
sudo apt-get install opus-tools
sudo apt-get install libav-tools
```
3. Create "music" directory near main.py or specify other directory in settings.py
4. Place songs in that directory
3. Start the bot:
```
PYTHONIOENCODING=UTF-8 python3 main.py
```

### Installation (Windows):
The same steps from above, but install [ffmpeg](https://www.ffmpeg.org/download.html) instead aconv


### Authors:

Author: [liokor.com/@KoroLion](https://liokor.com/@KoroLion)

Discord.py library was used: [github.com/Rapptz/discord.py](https://github.com/Rapptz/discord.py)