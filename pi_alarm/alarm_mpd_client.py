from pi_alarm.talk_to_me import TalkToMe
from mpd import MPDClient


class AlarmMPDClient:
    def __init__(self):
        self.client = MPDClient()
        # network timeout in seconds (floats allowed), default: None
        self.client.timeout = 10
        # timeout for fetching the result of the idle command is handled seperately, default: None
        self.client.idletimeout = None
        self.client.connect("localhost", 6600)  # connect to localhost:6600
        self.current_playlist = 0
        self.next_playlist()

    def disconnect(self):
        self.client.close()
        self.client.disconnect()  # disconnect from the server

    def play_pause(self):
        status = self.client.status()
        if status['state'] == 'stop' or status['state'] == 'pause':
            self.client.play()
        else:
            self.client.pause()

    def stop(self):
        self.client.stop()

    def prev_song(self):
        self.client.previous()

    def next_song(self):
        self.client.next()

    def get_all_playlists(self) -> []:
        return list(map(lambda pl: pl['playlist'], self.client.listplaylists()))

    '''
        Seeing as MPD does not keep a reference to the playlist loaded (the playlist is simply loaded to the end of the queue),
        the current playlist name is kept in memory and missing on startup.
        Next playlist therefore means comparing the stored current playlist name to all playlists available and loading the next in the list.
        If no playlist is yet in memory, the first playlist is loaded. Note that MPD will still have the previous playlist loaded but it is
        not possible to know which one it is without some sort of additional persistence layer like a file or a DB
    '''

    def next_playlist(self):
        all_playlists = self.get_all_playlists()
        playlist_count = len(all_playlists)
        # if there are no playlist
        if playlist_count > 0:
            playlist_index = None
            try:
                # Add one to the index of the current playlist and cycle back to the beginning if needed using modulus
                playlist_index = (self.current_playlist + 1) % playlist_count
            except ValueError as e:
                # Set the first playlist as the current.
                playlist_index = 0
            next_playlist = all_playlists[playlist_index]
            self.client.clear()
            self.client.load(next_playlist)
            self.current_playlist = playlist_index
            TalkToMe.speak(all_playlists[self.current_playlist])
        else:
            TalkToMe.speak("There are no playlists loaded")

    def prev_playlist(self):
        all_playlists = self.get_all_playlists()
        playlist_count = len(all_playlists)
        # if there are no playlist
        if playlist_count > 0:
            playlist_index = None
            try:
                # Subtract one from the index of the current playlist and cycle back to the beginning if needed using modulus.
                # Add an extra playlist_count to prevent getting a negative index
                playlist_index = (self.current_playlist - 1 + playlist_count) % playlist_count
            except ValueError as e:
                # Set the first playlist as the current.
                playlist_index = 0
            next_playlist = all_playlists[playlist_index]
            self.client.clear()
            self.client.load(next_playlist)
            self.current_playlist = playlist_index
            TalkToMe.speak(all_playlists[self.current_playlist])
        else:
            TalkToMe.speak("There are no playlists loaded")
