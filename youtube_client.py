import os
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl


class Playlist(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title


class Song(object):
    def __init__(self, artist, track):
        self.artist = artist
        self.track = track


class YouTubeClient(object):
    def __init__(self, credentials_location):
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        self.all_song_info = {}
        api_service_name = "youtube"
        api_version = "v3"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            credentials_location, scopes)
        credentials = flow.run_console()
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        self.youtube_client = youtube_client

    def get_playlists(self):
        request = self.youtube_client.playlists().list(
            part="id, snippet",
            maxResults=50,
            mine=True
        )
        response = request.execute()

        playlists = [Playlist(item['id'], item['snippet']['title']) for item in response['items']]

        return playlists

    def get_videos_from_playlist(self, playlist_id, spotify_token):
        request = self.youtube_client.playlistItems().list(
            playlistId=playlist_id,
            part="id, snippet",
            maxResults=50
        )
        response = request.execute()
        for item in response['items']:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(
                item["snippet"]["resourceId"]["videoId"])
            # use youtube_dl to collect the song name & artist name
            video = youtube_dl.YoutubeDL({'quiet': True}).extract_info(
                youtube_url, download=False
            )
            song_name = video["track"]
            artist = video["artist"]

            print(f"{song_name}")
            if song_name is not None and artist is not None:
                # save all important info and skip any missing song and artist
                self.all_song_info[video_title] = {
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,

                    # add the uri, easy to get song to put into playlist
                    "spotify_uri": self.get_spotify_uri(song_name, artist, spotify_token)

                }

        return self.all_song_info

    def get_spotify_uri(self, song_name, artist, spotify_token):
        """Search For the Song"""
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        if len(songs) == 0: return None
        # only use the first song
        uri = songs[0]["uri"]

        return uri

    def get_artist_and_track_from_video(self, video_id):
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"

        video = youtube_dl.YoutubeDL({'quiet': True}).extract_info(
            youtube_url, download=False
        )

        artist = video['artist']
        track = video['track']

        return artist, track
