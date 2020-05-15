import requests
import urllib.parse
import json


class SpotifyClient(object):
    def __init__(self, api_token):
        self.api_token = api_token

    def search_song(self, artist, track):
        query = urllib.parse.quote(f'{artist} {track}')
        url = f"https://api.spotify.com/v1/search?q={query}&type=track"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )
        response_json = response.json()
        results = response_json['tracks']['items']
        if results:
            # let's assume the first track in the list is the song we want
            return results[0]['id']
        else:
            raise Exception(f"No song found for {artist} = {track}")

    def add_song_to_spotify(self, song_id,playlist_id):
        url = "https://api.spotify.com/v1/me/tracks"
        response = requests.put(
            url,
            json={
                "ids": [song_id]
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )

        return response.ok

    def create_playlist(self, spotify_user_id, spotify_token, playlist_name):
        """Create A New Playlist"""
        request_body = json.dumps({
            "name": playlist_name,
            "description": "All Liked Youtube Videos",
            "public": True
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            spotify_user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()

        # playlist id
        return response_json["id"]
