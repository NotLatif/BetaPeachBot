class it:
    nothing_changed = "Non è cambiato niente."
    done = "Fatto"
    module_not_enabled = "Questo modulo non è abilitato in questo canale"
    confirm = "Conferma"
    cancel = "Annulla"


    class slash: #slash command descriptions
        join_msg = "Cambia il messaggio di benvenuto"
        leave_msg = "Cambia il messaggio di addio"
        respond_perc = "Imposta la percentuale di risposta del bot int(0->100)"
        respond_to_bots = "Decidi se culobot può rispondere ad altri bot"
        respond_to_bots_perc = "Imposta la percentuale di probabilità di rispondere ad un bot int(0->100)"
        dictionary = "Mostra le parole conosciute dal bot"
        dictionary_add = "Aggiunge una parola al dizionario"
        dictionary_edit = "Modifica una parola del dizionario"
        dictionary_del = "Elimina una parola dal dizionario"
        dictionary_use_global = "Attiva/Disattiva il dizionario globale"
        chess = "Fai una partita di scacchi!"
        chess_layout = "Informazioni sui layout (FEN) delle scachiere"
        chess_designs = "Informazioni sui design delle scachiere"
        playlist = "Gestisci le playlist salvate"
        player_settings = "Regola le impostazioni del player"
        play = "Riproduci qualcosa! (Youtube & Spotify)"
        module_info = "Mostra lo stato dei moduli"
        module = "Attiva/Disattiva funzioni del bot"
        feedback = "Send a message to the developer!"
    
    class choices:
        description = "Choose a subcommand"
        info = "Info"
        add = "Add"
        edit = "Edit"
        remove = "Remove"
        render = "Render"
        shuffle = "Shuffle"
        precision = "Precision"
        all = "All Modules"
        reply = "Message Reply"
        chess = "Chess"
        music = "Music"

    class commands:
        join_msg_embed_title = "Messaggio di benvenuto"
        join_msg_embed_desc = lambda isEnabled, msg: f"Enabled: {isEnabled}\nMessage: {msg}"

        leave_msg_embed_title = "Messaggio di addio"
        leave_msg_embed_desc = lambda isEnabled, msg: f"Enabled: {isEnabled}\nMessage: {msg}"

        resp_info = lambda percent: f"Rispondo il {percent}% delle volte"
        resp_to_bots_info = lambda isEnabled, percent : f"Risposta ai bot: {isEnabled}\nRispondo il {percent}% delle volte"
        resp_to_bots_edit = lambda percent: f"ok, risponderò il {percent}% delle volte ai bot"
        resp_newperc = lambda percent: f"ok, risponderò il {percent}% delle volte"
        resp_resp_to_bots_affirmative = "Ok, risponderò ai bot!"
        resp_resp_to_bots_negative = "Ok, non risponderò ai bot!"

        words_id_not_found = "Id parola non trovato, `/dictionary` per la lista di parole"
        words_learned = "Nuova parola imparata!"
        words_info = lambda guildName: f"Comandi disponibili:\n`/dictionary del <x>` per eliminare una parola\n`/dictionary edit <x> <parola>` per cambiare una parola\n`/dictionary add <parola>` per aggiungere una parola nuova\n`/dictionary del <id>` per rimuovere una parola nuova\n`/dictionary useDefault [true|false]` per scegliere se usare le parole globali\neg: `/dictionary add il culo, i culi` < per un esperienza migliore specifica l'articolo e la forma singolare(plurale)\neg: `/dictionary add culo` < specificare le forme non è obbligatorio\n**Puoi modificare solo le parole di {guildName}.**"
        words_use_global_words = lambda guildName: f"\n**{guildName} non usa le parole globali, quindi non verranno mostrate**, per mostrarle usare il comando: `/dictionary useDefault `"
        words_known_words = "Ecco le parole che conosco: "
        words_bot_words = "Prole del bot:"
        words_guild_words = lambda guildName: f"Prole di {guildName}:"

        module_info_embedTitle = lambda guildName: f"CuloBot modules for {guildName}"
        module_info_embedDesc = "You can change this data using the command /module <module> [#channel] [enable]"
        module_info_no_blacklisted = "No blacklisted channels"

        module_disabled_in_channel = lambda moduleName: f"Il modulo {moduleName} è disabilitato per:\n"
        module_disabled_all_channels = lambda moduleName: f"Module {moduleName} was disabled for every channel"
        module_enabled_all_channels = lambda moduleName: f"Module {moduleName} was enabled for every channel"
        module_already_disabled = lambda moduleName, channel: f"Module {moduleName} was already disabled for {channel}"
        module_already_enabled = lambda moduleName, channel: f"Module {moduleName} was already enabled for {channel}"
        module_now_disabled = lambda moduleName, channel: f"Module {moduleName} is now disabled for {channel}"
        module_now_enabled = lambda moduleName, channel: f"Module {moduleName} is now enabled for {channel}"
        module_arg_missing = "You have to select a value for the 'enable' variable when enabling/disabling every module at once.\nIf you want infos about the modules use /module-info"
        module_done = "Done, use /module-info if you want to see the changes\n"
        module_error = "There was an unknown error, please report this issue 0x1000"

    class chess:
        layout_description = "Scacchiere disponibili:"
        layout_global_layouts = "Scacchiere globali:"
        layout_guild_layouts = lambda guildName: f"Scacchiere di {guildName}:"
        layout_render_error = "Qualcosa è andato storto, probabilmente il FEN è errato"
        layout_render_invalid = "Invalid board"
        layout_render_select = "Seleziona il layout"
        layout_add_exists = "La schacchiera esiste già, usa\n`/chess-layouts` per vedere le scacchiere\n`/chess-layout edit` per modificare una scacchiera"
        layout_add_done = lambda name, fen: f"Ho aggiunto {name} {fen} !"
        layout_edit_select = "Seleziona il layout da modificare"
        layout_edit_title = lambda name: f"Modifica il layout {name}"
        layout_edit_ok = lambda name, fen: f"Ho modificato il FEN {name} -> {fen}"
        layout_delete_ok = lambda name, fen: f"Ho eliminato {name}, {fen}"
        layout_delete_select = "Scegli il layout da eliminare"
        layout_no_layouts = "Non esiste nessun layout del server"
        layout_user_rendered = lambda userName, fen: f"{userName} ha renderizzato il layout {fen}"
        
        design_available = "Design disponibili: "
        design_generated = lambda username, design: f"{username} ha generato il design {design}"
        design_404 = "Design non trovato, usa `!chess design` per vedere i design disponibili"
        design_render_select = "Seleziona il design"
        design_add_exists = "Il design esiste già, per modificarlo usa /chess-designs edit"
        design_add_done = lambda name, colors: f"Design aggiunto: **{name}**: {colors}"
        design_no_designs = "Non esiste nessun design del server"
        design_edit_title = lambda name: f"Modifica il design {name}"
        design_edit_ok = lambda name, colors: f"Ho modificato il design {name} -> {colors}"
        design_edit_select = "Scegli il design da modificare"
        design_delete_select = "Scegli il design da eliminare"
        design_delete_ok = lambda name, colors: f"Ho eliminato {name}, {colors}"
        design_HEX_invalid = lambda col1, col2: f"HEX non valido: {col1} {col2}"
        design_btn_confirm_response = "You have to choose a design and layout"

        embedTitle_fen_king_missing = "Problema con il FEN: manca il Re!"
        embedDesc_fen_king_missing = lambda black, white: f"Re mancante: {black} {white}"

        challenge_e1t = lambda challengeName, userName: f"{challengeName}, sei stato sfidato da {userName}!\nUsate una reazione per unirti ad un team (max 1 per squadra)"
        challenge_e2t = lambda challengeName, userName: f"{challengeName}, siete stati sfidati da {userName}!\nUno di voi può unirsi alla partita!"
        challenge_e3t = "Cerco giocatori per una partita di scacchi! ♟,\nUsa una reazione per unirti ad un team (max 1 per squadra)"
        challenge_ed = lambda gameFEN, designName: f"Scacchiera: {gameFEN}, design: {designName}"
        challenge_f = lambda userName: f"Partita richiesta da {userName}"
        challenge_s = lambda userName, userMention: f"{userName} Ha sfidato {userMention} a scacchi!"

        stop_title = "Ricerca Annullata"

        p_join = lambda player, rx: f"\n{player} si è unito a {rx}!"
        p2_join = lambda player, rx: f"\n{player} si è unito a {rx}!\nGenero la partita ..."

        not_enough_players = "Non ci sono abbastanza giocatori."
        found_players_t = lambda r1, p1, p2, r2: f"Giocatori trovati\n{r1} {p1} :vs: {p2} {r2}"
        found_players_d = lambda gameFEN, gameDesign: f"Impostazioni:\n- Scacchiera: {gameFEN}, Design: {gameDesign}"

        insert_design = "Inserisci un nuovo designo"

    class music:
        embedTitle_playlist_saved = lambda guildName: f"Saved playlists for {guildName}"
        embedDesc_playlist_saved = "Puoi salvare più link in una playlist in modo da non dover rifare gli stessi comandi più volte!"
        playlist_edit_select = "Scegli la playlist da modificare"
        playlist_edit_title = lambda playlistName: f"Cambia i link di {playlistName}"
        playlist_delete_ok = lambda playlistName, links: f"Ho eliminato {playlistName}, {links}"
        playlist_delete_select = "Scegli la playlist da eliminare"
        playlist_404 = "Non esiste nessuna playlist del server"
        newplaylist_tp = "Inserisci i link o i nomi delle canzoni uno per riga (spotify/youtube, anche playlist)"
        input_error = "C'è stato un errore con il tuo input"

        playlist_create_title = "Crea una nuova playlist"
        playlist_create_404 = lambda playlistName: f"Error: Could not find song/playlist {playlistName}\n"
        playlist_create_failed = "Error: every song/playlist failed"

        settings_embed_title = "Impostazioni del musicbot"
        settings_arg_needed = "Per questa impostazione devi specificare un valore nel comando"
        settings_timeline_max = lambda val: f"\nIl valore massimo di precisione della timeline è: {val}"
        settings_timeline_min = f"\nIl valore minimo di precisione della timeline è: 0"
        settings_new_precision = lambda val: f"La precisione della timeline è stata impostata a {val}"

        play_user_not_in_vc = f"Devi essere in un canale vocale per usare questo comando"
        play_wrong_command = "Usa /add_song per aggiungere una nuova traccia"
        play_already_connected = "Sono già connesso in un altro canale vocale"
        play_error_404 = "C'è stato un errore nella ricerca della traccia"

        class player:
            generic_error = "C'è stato un errore"

class en:
    nothing_changed = "Nothing changed."
    done = "Done"
    module_not_enabled = "That module isn't enabled in this channel."
    confirm = "Confirm"
    cancel = "Cancel"

    class slash: #slash command descriptions
        join_msg = "Change the welcome message"
        leave_msg = "Change the leaving message"
        respond_perc = "Set the culobot's messages response percentage int(0->100)"
        respond_to_bots = "Choose whether CuloBot will respond to bots"
        respond_to_bots_perc = "Set the message responses to bots percentage int(0->100)"
        dictionary = "Shows the bot's known words"
        dictionary_add = "Adds a word to the dictionary"
        dictionary_edit = "Edits a word from the dictionary"
        dictionary_del = "Deletes a word from the dictionary"
        dictionary_use_global = "Enables/Disables the global dictionary"
        chess = "Start a chess game!"
        chess_layout = "Info about chessboard layouts (FEN)"
        chess_designs = "Info abot chessboard designs"
        playlist = "Manage saved playlists"
        player_settings = "Manage player settings"
        play = "Play some music! (Youtube & Spotify)"
        module_info = "Show modules status"
        module = "Enable/Disable bot functionalities"
        feedback = "Send a message to the developer!"
    
    class choices:
        description = "Choose a subcommand"
        info = "Info"
        add = "Add"
        edit = "Edit"
        remove = "Remove"
        render = "Render"
        shuffle = "Shuffle"
        precision = "Precision"
        all = "All Modules"
        reply = "Message Reply"
        chess = "Chess"
        music = "Music"

    class commands:
        join_msg_embed_title = "Welcome message"
        join_msg_embed_desc = lambda isEnabled, msg: f"Enabled: {isEnabled}\nMessage: {msg}"

        leave_msg_embed_title = "Goodbye message"
        leave_msg_embed_desc = lambda isEnabled, msg: f"Enabled: {isEnabled}\nMessage: {msg}"

        resp_info = lambda percent: f"I will answer {percent}% of times"
        resp_to_bots_info = lambda isEnabled, percent : f"Answer to bots: {isEnabled}\nFor the {percent}% of times"
        resp_to_bots_edit = lambda percent: f"ok, I'll answer {percent}% of times to bots"
        resp_newperc = lambda percent: f"ok, I'll answer {percent}% of times to users"
        resp_resp_to_bots_affirmative = "Ok, I'll answer to bots!"
        resp_resp_to_bots_negative = "Ok, I won't answer to bots!"

        words_id_not_found = "Word id not found, `/dictionary` to see the dictionary"
        words_learned = "New word learned!"
        words_info = lambda guildName: f"Available commands:\n`/dictionary del <x>` to delete a word\n`/dictionary edit <x> <word>` to edit a word\n`/dictionary add <word>` to add a new word\n`/dictionary del <id>` to delete a word\n`/dictionary useDefault [true|false]` to choose whether to use global words\neg: `/dictionary add culo`\n**You can only edit entries under {guildName}.**"
        words_use_global_words = lambda guildName: f"\n**{guildName} does not use global words, so I wont't show them**, To enable them use the command: `/dictionary useDefault true`"
        words_known_words = "Known words: "
        words_bot_words = "Global dictionary"
        words_guild_words = lambda guildName: f"{guildName}'s dictionary"

        module_info_embedTitle = lambda guildName: f"CuloBot modules for {guildName}"
        module_info_embedDesc = "You can change this data using the command /module <module> [#channel] [enable]"
        module_info_no_blacklisted = "No blacklisted channels"

        module_disabled_in_channel = lambda moduleName: f"The module {moduleName} is disabled for:\n"
        module_disabled_all_channels = lambda moduleName: f"Module {moduleName} was disabled for every channel"
        module_enabled_all_channels = lambda moduleName: f"Module {moduleName} was enabled for every channel"
        module_already_disabled = lambda moduleName, channel: f"Module {moduleName} was already disabled for {channel}"
        module_already_enabled = lambda moduleName, channel: f"Module {moduleName} was already enabled for {channel}"
        module_now_disabled = lambda moduleName, channel: f"Module {moduleName} is now disabled for {channel}"
        module_now_enabled = lambda moduleName, channel: f"Module {moduleName} is now enabled for {channel}"
        module_arg_missing = "You have to select a value for the 'enable' variable when enabling/disabling every module at once.\nIf you want infos about the modules use /module-info"
        module_done = "Done, use /module-info if you want to see the changes\n"
        module_error = "There was an unknown error, please report this issue 0x1000"

    class chess:
        layout_description = "Available layouts:"
        layout_global_layouts = "Global layouts:"
        layout_guild_layouts = lambda guildName: f"{guildName}'s layouts:"
        layout_render_error = "Something went wrong, the FEN syntax is probably wrong"
        layout_render_invalid = "Invalid board"
        layout_render_select = "Select a layout"
        layout_add_exists = "Layout already exists, use\n`/chess-layouts` to see the chessboars layouts\n`/chess-layout edit` to edit a layout"
        layout_add_done = lambda name, fen: f"I added {name} {fen} !"
        layout_edit_select = "Select the layout to edit"
        layout_edit_title = lambda name: f"Edit the layout {name}"
        layout_edit_ok = lambda name, fen: f"I edited this FEN {name} -> {fen}"
        layout_delete_ok = lambda name, fen: f"I deleted {name}, {fen}"
        layout_delete_select = "Select the layout to delete"
        layout_no_layouts = "This server has no custom layouts"
        layout_user_rendered = lambda userName, fen: f"{userName} rendered layout {fen}"
        
        design_available = "Available designs: "
        design_generated = lambda username, design: f"{username} genereated the design {design}"
        design_404 = "Design not found, use`!chess design` to see the available designs"
        design_render_select = "Select a design"
        design_add_exists = "Design already exists, use `/chess-designs edit` to edit it"
        design_add_done = lambda name, colors: f"Design added: **{name}**: {colors}"
        design_no_designs = "This server has no custom deisgns"
        design_edit_title = lambda name: f"Edit design {name}"
        design_edit_ok = lambda name, colors: f"I edited the design {name} -> {colors}"
        design_edit_select = "Select the design to edit"
        design_delete_select = "Select the design to delete"
        design_delete_ok = lambda name, colors: f"I deleted {name}, {colors}"
        design_HEX_invalid = lambda col1, col2: f"HEX not valid: {col1} {col2}"
        design_btn_confirm_response = "You have to choose a design and layout"

        embedTitle_fen_king_missing = "FEN ERROR: Missing king!"
        embedDesc_fen_king_missing = lambda black, white: f"Missing king: {black} {white}"

        challenge_e1t = lambda challengeName, userName: f"{challengeName}, you're challenged at a chess game by {userName}!"
        challenge_e2t = lambda challengeName, userName: f"{challengeName}, you're challenged at a chess game by {userName}!\nOne of you can may the game!"
        challenge_e3t = "Looking for chess players! ♟,\nUse a reaction to join the game (max 1 player for team)"
        challenge_ed = lambda gameFEN, designName: f"layout: {gameFEN}, design: {designName}"
        challenge_f = lambda userName: f"Game started by {userName}"
        challenge_s = lambda userName, userMention: f"{userName} challenged {userMention} to a chess game!"

        stop_title = "Matchmaking cancelled"

        p_join = lambda player, rx: f"\n{player} joined {rx}!"
        p2_join = lambda player, rx: f"\n{player} joined {rx}!\nLoading game ..."

        not_enough_players = "Not enough players."
        found_players_t = lambda r1, p1, p2, r2: f"Players found\n{r1} {p1} :vs: {p2} {r2}"
        found_players_d = lambda gameFEN, gameDesign: f"Seggings:\n- Layout: {gameFEN}, Design: {gameDesign}"

        insert_design = "Insert a new design"

    class music:
        embedTitle_playlist_saved = lambda guildName: f"Saved playlists for {guildName}"
        embedDesc_playlist_saved = "You may save links for many playlists or songs so that you don't have to add them manually every time"
        playlist_edit_select = "Select the playlist to edit"
        playlist_edit_title = lambda playlistName: f"Change links for {playlistName}"
        playlist_delete_ok = lambda playlistName, links: f"I deleted {playlistName}, {links}"
        playlist_delete_select = "Select the playlist to delete"
        playlist_404 = "This server has no custom playlists"
        newplaylist_tp = "Insert song links one for each new line (spotify/youtube, playlists, albums and tracks)"
        input_error = "Input error"

        playlist_create_title = "Create a new playlist"
        playlist_create_404 = lambda playlistName: f"Error: Could not find song/playlist {playlistName}\n"
        playlist_create_failed = "Error: every song/playlist failed"

        settings_embed_title = "Musicbot settings"
        settings_arg_needed = "You must specify a value for this setting"
        settings_timeline_max = lambda val: f"\nmax timeline precision is now : {val}"
        settings_timeline_min = f"\nMin timeline precision is: 0"
        settings_new_precision = lambda val: f"The timeline precision was set to {val}"

        play_user_not_in_vc = f"You must be in a voice channel to use this command"
        play_wrong_command = "Use /add_song to add to the queue"
        play_already_connected = "I'm already connected in another voice channel"
        play_error_404 = "There was an error with this track"

        class player:
            generic_error = "There was an error."