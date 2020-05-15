import os
import json
import requests
from spotify_client import SpotifyClient
from youtube_client import YouTubeClient


def run():
    #Take user inputs
    username = input("Enter your Spotify Username: ")
    sToken = input("Enter your Spotify token: ")
    playlist_name = input("Enter desired playlist title: ")
    youtube_client = YouTubeClient('./creds/client_secret.json')
    spotify_client = SpotifyClient(sToken)
    playlists = youtube_client.get_playlists()

    for index, playlist in enumerate(playlists):
        print(f"{index}: {playlist.title}")
    choice = int(input("Enter your choice: "))
    chosen_playlist = playlists[choice]
    print(f"You selected: {chosen_playlist.title}")

    songs = youtube_client.get_videos_from_playlist(chosen_playlist.id,sToken)
    playlist_id = spotify_client.create_playlist(username,sToken,playlist_name)
    print(f"Attempting to add {len(songs)}")

    uris = [info["spotify_uri"]
                for song, info in songs.items()]
    uris = list(filter(None, uris))
    request_data = json.dumps(uris)
    query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)

    response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(sToken)
            }
        )
    print(f"Succefully added {len(uris)} songs!")

if __name__ == '__main__':
    run()
