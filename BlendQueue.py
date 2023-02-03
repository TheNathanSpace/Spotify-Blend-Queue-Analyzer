import json
from pathlib import Path

import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from cache.secrets import client_id, client_secret, username, blend_playlist


def clean_path_child(original_path):
    invalid_chars = '\/:*?"<>|'
    for char in invalid_chars:
        original_path = original_path.replace(char, '_')

    return original_path


if __name__ == '__main__':
    spotify_scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative user-library-read"

    (Path.cwd() / "cache").mkdir(exist_ok = True)

    auth_manager = SpotifyOAuth(client_id = client_id,
                                client_secret = client_secret,
                                redirect_uri = "https://example.com", scope = spotify_scope,
                                cache_path = str(Path.cwd() / "cache" / "spotify_token_cache.json"),
                                username = username)
    spotipy: Spotify = spotipy.Spotify(auth_manager = auth_manager)

    # Get the currently playing device
    devices = spotipy.devices()["devices"]
    current_device = None
    for device in devices:
        if device["is_active"]:
            current_device = device["id"]
            break
    if current_device is None:
        print("Error: Spotify not currently playing on any device.")
        exit(-1)

    # Get user playlists
    playlists = spotipy.current_user_playlists()
    user_playlists = {}
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            playlist_name = clean_path_child(playlist['name'])
            user_playlists[playlist['uri']] = playlist_name

        if playlists['next']:
            playlists = spotipy.next(playlists)
        else:
            playlists = None

    # Get Blend playlist
    blend_playlist_uri = None
    for uri in user_playlists:
        if blend_playlist in uri:
            blend_playlist_uri = uri
            break
    if blend_playlist_uri is None:
        print("Error: Specified Blend playlist not found in user profile.")
        exit(-1)

    # Get Blend playlist tracks
    playlist_tracks = []
    results = spotipy.playlist_items(playlist_id = blend_playlist_uri, fields = "items.track.uri, next")
    tracks = results['items']
    while results['next']:
        results = spotipy.next(results)
        tracks.extend(results['items'])
    index = 0
    for track in tracks:
        tracks_dict = tracks[index]['track']
        track_uri = tracks_dict["uri"]
        playlist_tracks.append(track_uri)
        index += 1

    # perform 20 trials
    trials = []
    trials_indices = []
    for i in range(0, 20):
        spotipy.shuffle(state = True)
        spotipy.start_playback(device_id = current_device, context_uri = blend_playlist_uri)
        user_queue = spotipy.queue()
        this_queue = []
        this_queue_indices = []
        this_queue.append(user_queue["currently_playing"]["uri"])
        this_queue_indices.append(playlist_tracks.index(user_queue["currently_playing"]["uri"]))
        for item in user_queue["queue"]:
            this_queue.append(item["uri"])
            this_queue_indices.append(playlist_tracks.index(item["uri"]))

        trials.append(this_queue)
        trials_indices.append(this_queue_indices)

    (Path().cwd() / "output.json").touch(exist_ok = True)
    (Path().cwd() / "output.json").write_text(
        json.dumps({"trials": trials, "trials_indices": trials_indices}, indent = 4))
