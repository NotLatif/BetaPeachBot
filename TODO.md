# CRITICAL
spotipy in spotifyParser causes heartbeat block, switch to an async module ASAP
possible alternatives: https://pypi.org/project/async-spotify/

# Culobot features

✅ add possibility to whitelist channels for modules

✅ guild count

🟦 add default permissions

🟦 add slash commands with musicbot

🟦 Warn users that try to start the bot when it's already on in another text/voice chat

🟦 Command to change language

🟦 Command for other_perc

🟦 speed pitch effects(filters nightcore, filters bassboost, filters list, filters reset)

🟦 Finish lang.json

# Culobot bugs

✅ prevent users that are not in the audiochat to use embed buttons for musicbot

✅ restart: ripete la traccia

✅ bug where thumbnails are abot the previous song / embed is frozen / other bug related to the queue embed
    how to reproduce:
    - use a playlist with enough tracks
    - join a vc and use the /play command to start the playlist
    - move in another channel and move the bot using the discord "move to channel"
    - the bot should stil be working but now the embed is frozen
    - try to restart the queue using the !queue command [maybe you need to let the bot start a new track before idk]
    - The bug should appear
    - The embed message will only update if you interact with it (for example skipping)

✅ Aggiungere una canzone alla volta fa cose strane allo shuffle (seems to have been fixed by accident)

🟦 
av_interleaved_write_fram(): Broken pipe
./bot-start: line 2: 1298 Killed
Error writing trailer of pipe:1: Broken pipe
./bot-start: line 3: n3.9: command not found

🟦 there are too many files in the main folder, reorganize?

🟦 inform user when bot can't find song (404 in musicPlayer.py)

🟦 fix suggest command

🟦 graphical bug while skipping with 1 song loop

🟦 Raramente può capitare che queue e canzoni in riproduzione si desincronizzano???? (Bug copia.txt)

🟥 reorganize musicPlayer.MessageHandler.getEmbed()

# Code things

🟥 Make settings a local variable under MyBot class

-----legenda-----
✅ Done/Fixed (resets with every release)
🟧 Test needed
🟦 TO DO/CHECK
🟥 wontdo (for now)